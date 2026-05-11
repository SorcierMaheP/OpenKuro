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


@tool(
    name="write",
    description="Write text content to a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to write"},
            "content": {
                "type": "string",
                "description": "Text content to write to the file",
            },
        },
        "required": ["path", "content"],
    },
)
# Write text to a file and return status
async def write_file(path: str, content: str, session: "AgentSession") -> str:
    try:
        Path(path).write_text(content)
        return f"Success writing text to file at {path}"
    except PermissionError:
        return f"Error: Permission denied writing to {path}"
    except IsADirectoryError:
        return f"Error: Specified path is a directory at {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool(
    name="edit",
    description="Edit a file by replacing a string",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file to write"},
            "old_text": {
                "type": "string",
                "description": "Old text that needs to be replaced",
            },
            "new_text": {
                "type": "string",
                "description": "Newer text to be replaced with",
            },
        },
        "required": ["path", "old_text", "new_text"],
    },
)
# Replace old text with new text and return status
async def edit_file(
    path: str, old_text: str, new_text: str, session: "AgentSession"
) -> str:
    try:
        old_content = Path(path).read_text()

        if old_text not in old_content:
            return f"Error: '{old_text} not found in {path}"

        new_content = old_content.replace(old_text, new_text)
        Path(path).write_text(new_content)
        return f"Successfully edited file at {path}"
    except FileNotFoundError:
        return f"Error: File not found at {path}"
    except PermissionError:
        return f"Error: Permission denied editing file at {path}"
    except IsADirectoryError:
        return f"Error: Specified path is a directory at {path}"
    except Exception as e:
        return f"Error editing file: {e}"


# Tool to run shell commands
@tool(
    name="bash",
    description="Runs a bash shell command",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Name of command to execute"}
        },
        "required": ["command"],
    },
)
# Run a bash command and return the output
async def bash(command: str, session: "AgentSession") -> str:
    try:
        # Spawns a new shell with specified command
        # stdout and stderr are pipes so that python can capture them
        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = (
            await process.communicate()
        )  # Result is in bytes hence need to decode

        output = stdout.decode() if stdout else ""
        error = stderr.decode() if stderr else ""

        if output and error:
            return f"{output}\n{error}"
        return output or error or "Command completed with no output or error"
    except Exception as e:
        return f"Error executing command: {e}"
