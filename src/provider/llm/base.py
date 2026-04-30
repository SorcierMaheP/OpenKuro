# LLM Provider settings with litellm

from dataclasses import dataclass
from typing import Any, Optional, cast

from litellm import acompletion, Choices, TYPE_CHECKING
from litellm.types.completion import ChatCompletionMessageParam as Message

if TYPE_CHECKING:
    from src.utils.config import LLMConfig


# Define a schema class for LLM Tool Call
@dataclass
class LLMToolCall:
    id: str
    name: str
    arguments: str  # This will be a JSON string


class LLMProvider:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        api_base: Optional[str] = None,
        temp: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.temp = temp
        self.max_tokens = max_tokens
        self._settings = kwargs

    # Create a provider from LLMConfig
    @classmethod
    def from_config(cls, config: "LLMConfig") -> "LLMProvider":
        return cls(
            provider=config.provider,
            model=config.model,
            api_key=config.api_key,
            api_base=config.api_base,
            temp=config.temp,
            max_tokens=config.max_tokens,
        )

    # Async func to call LLM with messages
    # Pass a list of tool definitions as well
    async def chat(
        self,
        messages: list[Message],
        tools: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> tuple[str, list[LLMToolCall]]:
        request_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "api_key": self.api_key,
        }

        if self.api_base:
            request_kwargs["api_base"] = self.api_base

        if tools:
            request_kwargs["tools"] = tools

        # Add extra kwargs
        request_kwargs.update(kwargs)

        response = await acompletion(**request_kwargs)
        message = cast(
            Choices, response.choices[0]
        ).message  # Select the first choice from multiple possible completions

        # Returns message and list of possible tool calls
        return (
            message.content or "",
            [
                LLMToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                )
                for tc in (message.tool_calls or [])
            ],
        )
