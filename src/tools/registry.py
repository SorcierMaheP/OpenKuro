# Code for tool registry to manage available tools

from typing import TYPE_CHECKING, Any

from src.tools.base import BaseTool
from src.tools.builtin_tools import read_file, write_file, edit_file, bash

if TYPE_CHECKING:
    from src.core.agent import AgentSession


# Define a registry class for tools
class ToolRegistry:

    # Initialise registry
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_all(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        return [tool.get_tool_schema() for tool in self._tools.values()]

    async def execute_tool(
        self, name: str, session: "AgentSession", **kwargs: Any
    ) -> str:
        tool = self.get_tool(name)

        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        return await tool.execute(session=session, **kwargs)

    # Create a tool registry with builtin tools already imported and registered
    @classmethod
    def with_builtins(cls) -> "ToolRegistry":

        registry = cls()  # An instance of the class, __init__ will be called here

        registry.register_tool(read_file)
        registry.register_tool(write_file)
        registry.register_tool(edit_file)
        registry.register_tool(bash)

        return registry
