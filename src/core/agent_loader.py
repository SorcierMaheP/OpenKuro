# Agent def loader
from typing import Any
from pydantic import BaseModel, ValidationError

from utils.config import LLMConfig, Config
from utils.def_loader import DefNotFoundError, InvalidDefError, parse_definition


# Loaded agent definition schema with merged settings
class AgentDef(BaseModel):
    id: str
    name: str
    description: str = ""
    agent_md: str
    llm: LLMConfig


# Load agent definitions from AGENT.md files
class AgentLoader:

    def __init__(self, config: Config):
        self.config = config

    @staticmethod
    def from_config(config: Config) -> "AgentLoader":
        return AgentLoader(config)

    # Load agent from their ID
    def load(self, agent_id: str) -> AgentDef:
        agent_file = self.config.agents_path / agent_id / "AGENT.md"
        if not agent_file.exists():
            raise DefNotFoundError("agent", agent_id)

        try:
            content = agent_file.read_text()
            agent_def = parse_definition(content, agent_id, self._parse_agent_def)
        except InvalidDefError:
            raise
        except Exception as e:
            raise InvalidDefError("agent", agent_id, str(e))

        return agent_def

    # Actual parse func, used in parse_definition function as arg
    # Parse agent def from frontmatter
    def _parse_agent_def(
        self, def_id: str, frontmatter: dict[str, Any], body: str
    ) -> AgentDef:
        llm_overrides = frontmatter.get("llm")
        merged_llm = self._merge_llm_config(llm_overrides)

        try:
            return AgentDef(
                id=def_id,
                name=frontmatter["name"],
                description=frontmatter.get("description", ""),
                agent_md=body.strip(),
                llm=merged_llm,
            )
        except ValidationError as e:
            raise InvalidDefError("agent", def_id, str(e))

    # Merge agent's LLM config with global defaults
    # base is the global default, agent_llm will be the overrides from the AGENT.md file
    def _merge_llm_config(self, agent_llm: dict[str, Any] | None) -> LLMConfig:
        base = self.config.llm.model_dump()
        if agent_llm:
            base = {**base, **agent_llm}
        return LLMConfig(**base)
