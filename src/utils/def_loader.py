# Will be used to load definition files like agents, skills, crons

import logging
from pathlib import Path
from typing import Any, Callable, TypeVar
import yaml

T = TypeVar("T")  # Generic type
logger = logging.getLogger(__name__)  # Logger based on current file name


class DefNotFoundError(Exception):
    def __init__(self):
        pass


class InvalidDefError(Exception):
    def __init__(self):
        pass


def parse_definition():
    pass


def discover_definition():
    pass


def write_definition():
    pass
