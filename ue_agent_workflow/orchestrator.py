"""多 Agent 编排引擎"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ue_agent_workflow.config import Config
from ue_agent_workflow.llm import create_llm
from ue_agent_workflow.agents import RequirementAgent, DesignAgent, TechAgent, QAAgent
from ue_agent_workflow.context import AgentContext


@dataclass
class ProjectBrief:
    title: str
    style: str
    scenario_desc: str
    assets: list[str] = field(default_factory=list)
    interactive_features: list[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    brief: ProjectBrief
    tasks: list[dict] = field(default_factory=list)
    style_notes: str = ""
    design_output: str = ""
    tech_output: str = ""
    qa_output: str = ""
    generated_files: list[str] = field(default_factory=list)
    context: AgentContext | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "project": self.brief.title,
            "style": self.style_notes or self.brief.style,
            "timestamp": self.timestamp,
            "tasks": self.tasks,
            "design_output": self.design_output[:500] if self.design_output else "",
            "tech_output": self.tech_output[:500] if self.tech_output else "",
            "qa_output": self.qa_output[:500] if self.qa_output else "",
            "generated_files": self.generated_files,
        }


class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.llm = create_llm(config)
        self.requirement = RequirementAgent(self.llm)
        self.design = DesignAgent(self.llm)
        self.tech = TechAgent(self.llm)
        self.qa = QAAgent(self.llm)

    def run(self, brief: ProjectBrief) -> WorkflowResult:
        result = WorkflowResult(brief=brief)

        # Step 1: 需求理解
        print(f"\n{'='*50}")
        print(f"  [Step 1/4] {self.requirement.name} — 分析需求")
        print(f"{'='*50}")
        tasks, style_notes, context = self.requirement.process(
            title=brief.title,
            style=brief.style,
            scenario_desc=brief.scenario_desc,
            assets=brief.assets,
            features=brief.interactive_features,
        )
        result.tasks = tasks
        result.style_notes = style_notes
        result.context = context
        print(f"  → 拆解为 {len(tasks)} 个子任务")

        # Step 2: 设计 Agent
        print(f"\n{'='*50}")
        print(f"  [Step 2/4] {self.design.name} — 视觉设计")
        print(f"{'='*50}")
        for task in tasks:
            if task["type"] in ("visual",):
                result.design_output = self.design.process(task["description"], context)
                print(f"  → 设计完成")
        result.generated_files = list(context.output_files)

        # Step 3: 技术 Agent
        print(f"\n{'='*50}")
        print(f"  [Step 3/4] {self.tech.name} — 技术实现")
        print(f"{'='*50}")
        for task in tasks:
            if task["type"] in ("asset", "blueprint"):
                output = self.tech.process(task["description"], context)
                result.tech_output += output + "\n"
        result.generated_files = list(context.output_files)

        # Step 4: 质检 Agent
        print(f"\n{'='*50}")
        print(f"  [Step 4/4] {self.qa.name} — 质量评审")
        print(f"{'='*50}")
        result.qa_output = self.qa.process(context)
        print(f"  → 评审完成")

        # 保存结果
        self._save_result(result)

        return result

    def _save_result(self, result: WorkflowResult):
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        report_path = output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n  📄 报告已保存: {report_path}")
