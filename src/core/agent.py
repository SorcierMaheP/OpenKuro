# Core agent and agent session code
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from litellm.types.completion import ChatCompletionMessageParam as Message

from src.provider.llm import LLMProvider
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
        session = AgentSession(agent=self, state=state)
        return session


# Works with swappable session state
@dataclass
class AgentSession:
    agent: Agent
    state: SessionState
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def session_id(self) -> str:
        return self.state.session_id

    # Sends a message to the LLM and gets a response
    async def chat(self, message: str) -> str:
        user_msg: Message = {"role": "user", "content": message}
        self.state.add_message(user_msg)

        messages = self.state.build_messages()
        response = await self.agent.llm.chat(messages)

        assistant_msg: Message = {"role": "assistant", "content": response}
        self.state.add_message(assistant_msg)

        return response
