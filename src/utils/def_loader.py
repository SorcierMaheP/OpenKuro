# Will be used to load definition files like agents, skills, crons

import logging
from pathlib import Path
from typing import Any, Callable, TypeVar
import yaml

T = TypeVar("T")  # Generic type
logger = logging.getLogger(__name__)  # Logger based on current file name


# Def folder/file does not exist
class DefNotFoundError(Exception):
    def __init__(self, kind: str, def_id: str):
        super().__init__(f"{kind.capitalize()} not found: {def_id}!")
        self.kind = kind
        self.def_id = def_id


# Def file has problems
class InvalidDefError(Exception):
    def __init__(self, kind: str, def_id: str, reason: str):
        super().__init__(f"Invalid {kind} due to {reason}: {def_id}!")
        self.kind = kind
        self.def_id = def_id
        self.reason = reason


# Parses YAML definition with type conversion
# Parse func should be a callable(like a function) which takes a str, a dict and another str as args and returns T(generic type) as output
def parse_definition(
    content: str, def_id: str, parse_func: Callable[[str, dict[str, Any], str], T]
) -> T:

    # If no frontmatter
    if not content.startswith("---\n"):
        body = content
        return parse_func(def_id, {}, body)

    # Find frontmatter delimiters
    end_delimiter = content.find("\n---\n", 4)

    # If frontmatter is malformed
    if end_delimiter == -1:
        body = content
        return parse_func(def_id, {}, body)

    # Extract frontmatter and body separately
    frontmatter_text = content[4:end_delimiter]
    body = content[end_delimiter + 5 :]

    raw_dict = yaml.safe_load(frontmatter_text) or {}
    return parse_func(def_id, raw_dict, body)


# Search folder for def files
def discover_definition(
    path: Path,
    filename: str,
    parse_func: Callable[[str, dict[str, Any], str], T | None],
) -> list[T]:
    if not path.exists():
        logger.warning(f"Definitions folder not found at {path}!")
        return []

    results = []
    for def_dir in path.iterdir():
        if not def_dir.is_dir():
            continue

        def_file = def_dir / filename
        if not def_file.exists():
            logger.warning(f"No {filename} found in {def_dir.name}!")
            continue

        try:
            content = def_file.read_text()
            result = parse_definition(content, def_dir.name, parse_func)
            if result is not None:
                results.append(result)
        except Exception as e:
            logger.warning(f"Failed to parse {def_dir.name} due to {e}!")
            continue

    return results


# Write a def file with frontmatter and body specified
def write_definition(
    def_id: str,
    frontmatter: dict[str, Any],
    body: str,
    base_path: Path,
    filename: str,
) -> Path:
    def_dir = base_path / def_id
    def_dir.mkdir(parents=True, exist_ok=True)

    yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    content = f"---\n{yaml_content}---\n\n{body.strip()}\n"

    def_file = def_dir / filename
    def_file.write_text(content)

    return def_file
