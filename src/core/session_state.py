# dataclass automatically generates common methods for classes that mainly store data.
from dataclasses import dataclass

from typing import TYPE_CHECKING
from litellm.types.completion import ChatCompletionMessageParam as Message

if TYPE_CHECKING:
    from core.agent import Agent


# Container class to store the state of the chat session
@dataclass
class SessionState:
    session_id: str
    agent: "Agent"
    messages: list[Message]

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def build_messages(self) -> list[Message]:
        system_prompt = self.agent.agent_def.agent_md
        messages: list[Message] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.messages)
        return messages
