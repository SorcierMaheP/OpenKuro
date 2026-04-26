# LLM Provider settings with litellm

from typing import Any, Optional, cast

from litellm import acompletion, Choices, TYPE_CHECKING
from litellm.types.completion import ChatCompletionMessageParam as Message

if TYPE_CHECKING:
    from utils.config import LLMConfig


class LLMProvider:
    def __init__(
        self,
        model: str,
        api_key: str,
        api_base: Optional[str] = None,
        temp: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ):
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
            model=config.model,
            api_key=config.api_key,
            api_base=config.api_base,
            temp=config.temp,
            max_tokens=config.max_tokens,
        )

    # Async func to call LLM with messages
    async def chat(self, messages: list[Message], **kwargs: Any) -> str:
        request_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "api_key": self.api_key,
        }

        if self.api_base:
            request_kwargs["api_base"] = self.api_base

        # Add extra kwargs
        request_kwargs.update(kwargs)

        response = await acompletion(**request_kwargs)
        message = cast(
            Choices, response.choices[0]
        ).message  # Select the first choice from multiple possible completions

        return message.content or ""
