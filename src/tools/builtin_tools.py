# Define functions which will act as built-in tools for the agent

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from src.tools.base import tool  # The decorator function

if TYPE_CHECKING:
    from src.core.agent import AgentSession
