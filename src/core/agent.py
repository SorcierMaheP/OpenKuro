# Core agent and agent session code, with tool support
import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from litellm.types.completion import (
    ChatCompletionMessageParam as Message,
    ChatCompletionMessageToolCallParam,
)

from src.provider.llm import LLMProvider, LLMToolCall
from src.tools.registry import ToolRegistry
from src.core.session_state import SessionState

if TYPE_CHECKING:
    from src.core.agent_loader import AgentDef
    from src.utils.config import Config


# Agent class that creates and manages conversation sessions
class Agent:
    def __init__(self, agent_def: "AgentDef", config: "Config") -> None:
        self.agent_def = agent_def
        self.config = config
        self.llm = LLMProvider.from_config(agent_def.llm)

    def new_session(self, session_id: str | None = None) -> "AgentSession":
        session_id = session_id or str(uuid.uuid4())
        state = SessionState(session_id=session_id, agent=self, messages=[])

        # Create tool registry with builtin tools and pass it to AgentSession
        tools = ToolRegistry.with_builtins()
        session = AgentSession(agent=self, state=state, tools=tools)
        return session


# Works with swappable session state
@dataclass
class AgentSession:
    agent: Agent
    state: SessionState
    tools: ToolRegistry
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def session_id(self) -> str:
        return self.state.session_id

    # Sends a message to the LLM and gets a response
    async def chat(self, message: str) -> str:
        user_msg: Message = {"role": "user", "content": message}
        self.state.add_message(user_msg)

        tool_schemas = self.tools.get_tool_schemas()

        # Process in infinite loop till no more tool calls are left
        while True:
            messages = self.state.build_messages()
            content, tool_calls = await self.agent.llm.chat(messages, tool_schemas)

            # OpenAI schema for tool calls
            tool_call_dicts: list[ChatCompletionMessageToolCallParam] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in tool_calls
            ]

            assistant_msg: Message = {"role": "assistant", "content": content}
            if tool_call_dicts:
                assistant_msg["tool_calls"] = tool_call_dicts
            self.state.add_message(assistant_msg)

            if not tool_calls:
                break

            await self._handle_tool_calls(tool_calls)

        return content

    # Function to handle tool calls from LLM response
    async def _handle_tool_calls(self, tool_calls: list["LLMToolCall"]) -> None:
        # Run _execute_tool_call concurrently
        # asyncio gather expects all coroutines to be separate arguments, hence we are unpacking list with *
        tool_call_results = await asyncio.gather(
            *[self._execute_tool_call(tool_call) for tool_call in tool_calls]
        )

        for tool_call, result in zip(tool_calls, tool_call_results):
            # Build a message for tool call and corresponding result
            # Also save it in the state
            tool_msg: Message = {
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call.id,
            }
            self.state.add_message(tool_msg)

    # Function to execute a single tool call
    # Return type is str, check builtin tool function code
    async def _execute_tool_call(self, tool_call: LLMToolCall) -> str:
        try:
            args = json.loads(tool_call.arguments)
        except json.JSONDecodeError:
            args = {}

        try:
            result = await self.tools.execute_tool(
                name=tool_call.name, session=self, **args
            )
        except Exception as e:
            result = f"Error executing tool: {e}"

        return result
