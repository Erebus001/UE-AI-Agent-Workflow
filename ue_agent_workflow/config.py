"""配置管理"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Config:
    llm_provider: str = "claude"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250506"
    mimo_api_key: str = ""
    mimo_base_url: str = ""
    mimo_model: str = "mimo-v2.5-pro"
    openai_api_key: str = ""
    openai_base_url: str = ""
    ue_project_path: str = ""
    log_level: str = "INFO"

    @classmethod
    def load(cls, env_file: str | None = None) -> "Config":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "claude"),
            claude_api_key=os.getenv("CLAUDE_API_KEY", ""),
            claude_model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250506"),
            mimo_api_key=os.getenv("MIMO_API_KEY", ""),
            mimo_base_url=os.getenv("MIMO_BASE_URL", ""),
            mimo_model=os.getenv("MIMO_MODEL", "mimo-v2.5-pro"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
            ue_project_path=os.getenv("UE_PROJECT_PATH", ""),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def missing_keys(self) -> list[str]:
        missing = []
        if self.llm_provider == "claude" and not self.claude_api_key:
            missing.append("CLAUDE_API_KEY")
        if self.llm_provider == "mimo" and not self.mimo_api_key:
            missing.append("MIMO_API_KEY")
        if self.llm_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        return missing
