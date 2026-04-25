# Config management for the project

from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field, model_validator, HttpUrl

# Pydantic Models are simply classes which inherit from BaseModel and define fields as annotated attributes.


# Following is LLM Provider config
class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    api_base: HttpUrl | None = None
    temp: float = Field(
        default=0.7, ge=0.0, le=2.0
    )  # For chat completion temp goes to 2 for some reason
    max_tokens: float = Field(default=2048, ge=0)


# Main config stuff
class Config(BaseModel):
    workspace: Path
    llm: LLMConfig
    default_agent: str
    agents_path: Path = Field(default=Path("agents"))  # agents folder as default

    # After validators run after the whole model has been validated.
    @model_validator(mode="after")
    def resolve_paths(self) -> Self:
        for field_name in ("agents_path",):
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, self.workspace / path)
            return self

    # Loads config from directory
    @classmethod
    def load(cls, workspace_dir: Path) -> Self:
        config_data = cls._load_config(workspace_dir)
        config_data["workspace"] = workspace_dir
        return cls.model_validate(config_data)

    # Loads config from YAML file
    @classmethod
    def _load_config(cls, workspace_dir: Path) -> dict[str, Any]:
        config_file = workspace_dir / "config.user.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"Config file {config_file} not found!")

        with open(config_file) as f:
            return yaml.safe_load(f) or {}
