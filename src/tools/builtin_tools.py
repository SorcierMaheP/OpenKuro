# Define functions which will act as built-in tools for the agent

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from src.tools.base import tool  # The decorator function

if TYPE_CHECKING:
    from src.core.agent import AgentSession

# Filesystem tools to read, write, edit


@tool(
    name="read",
    description="Read the contents of a text file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to read"}
        },
        "required": ["path"],  # path is NEEDED for read function
    },
)
# Read and return the contents of specified file
async def read_file(path: str, session: "AgentSession") -> str:
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return f"Error: File not found at {path}"
    except PermissionError:
        return f"Error: Permission denied reading file at {path}"
    except IsADirectoryError:
        return f"Error: Specified path is a directory at {path}"
    except Exception as e:
        return f"Error reading file: {e}"
