"""Agent 间共享上下文"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """跨 Agent 共享状态"""
    style_guide: str = ""
    project_title: str = ""
    scenario_desc: str = ""
    generated_concepts: list[str] = field(default_factory=list)
    generated_assets: list[dict] = field(default_factory=list)
    blueprints: list[str] = field(default_factory=list)
    output_files: list[str] = field(default_factory=list)
    conversation_history: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_summary(self) -> str:
        lines = [f"项目: {self.project_title}"]
        if self.style_guide:
            lines.append(f"风格: {self.style_guide}")
        lines.append(f"概念图: {len(self.generated_concepts)} 张")
        lines.append(f"资产: {len(self.generated_assets)} 个")
        lines.append(f"蓝图: {len(self.blueprints)} 个")
        return "\n".join(lines)
