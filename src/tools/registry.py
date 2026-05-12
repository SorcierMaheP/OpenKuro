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
