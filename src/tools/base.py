# Interface and decorator to define tools

import asyncio
from abc import ABC, abstractmethod  # To create abstract classes and methods
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.core.agent import AgentSession


# Create an abstract base class for tools
class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]  # This will be JSON schema

    @abstractmethod
    async def execute(self, session: "AgentSession", **kwargs: Any) -> str:
        """Method to execute the tool"""

    # To get schema of current tool
    def get_tool_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# Create a decorator @tool to register a function as a tool
# Technically tool function returns the decorator func,
# hence its return type should be Callable[[Param type of decorator func], Return type of decorator func]
# which is Callable[[Callable], FunctionTool]
def tool(name: str, description: str, parameters: dict[str, Any]) -> Callable:

    def decorator(func: Callable) -> "FunctionTool":
        return FunctionTool(name, description, parameters, func)

    return decorator


# Wrapper class for tool created using @tool decorator
def FunctionTool(BaseTool):
    def __init__(
        self, name: str, description: str, parameters: dict[str, Any], func: Callable
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._func = func

    async def execute(self, session: "AgentSession", **kwargs: Any) -> str:
        result = self._func(session=session, **kwargs)

        # If func is async, await the result. If func is sync, this step is skipped
        if asyncio.iscoroutine(result):
            result = await result

        return str(result)
