# Interface and decorator to define tools

import asyncio
from abc import ABC, abstractmethod  # To create abstract classes and methods
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.core.agent import AgentSession
