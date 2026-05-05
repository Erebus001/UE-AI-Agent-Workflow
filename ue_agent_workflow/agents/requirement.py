"""需求理解 Agent — 解析项目 brief，拆解子任务"""
from ue_agent_workflow.agent_base import BaseAgent
from ue_agent_workflow.context import AgentContext
from ue_agent_workflow.llm import LLMClient

REQUIREMENT_SYSTEM_PROMPT = """你是一个 Unreal Engine 项目需求分析师。
你的职责是：
1. 理解用户的项目需求（标题、风格、场景描述、所需资产、交互功能）
2. 将需求拆解为具体的子任务
3. 返回 JSON 格式的任务列表

输出格式严格为 JSON：
{
  "tasks": [
    {"type": "visual", "description": "任务描述", "priority": 1},
    {"type": "asset", "description": "任务描述", "priority": 2},
    {"type": "blueprint", "description": "任务描述", "priority": 2},
    {"type": "qa", "description": "任务描述", "priority": 3}
  ],
  "style_notes": "风格要点总结"
}

type 可选: visual, asset, blueprint, qa
priority: 1-3 (数字越小优先级越高)
返回严格的 JSON，不要包含其他文字。
"""


class RequirementAgent(BaseAgent):
    def __init__(self, llm: LLMClient):
        super().__init__("需求理解Agent", llm, REQUIREMENT_SYSTEM_PROMPT)

    def process(self, title: str, style: str, scenario_desc: str,
                assets: list[str], features: list[str]) -> tuple[list[dict], str, AgentContext]:
        context = AgentContext()
        context.project_title = title
        context.style_guide = style
        context.scenario_desc = scenario_desc

        task_text = (
            f"项目标题: {title}\n"
            f"风格: {style}\n"
            f"场景描述: {scenario_desc}\n"
            f"所需资产: {', '.join(assets)}\n"
            f"交互功能: {', '.join(features)}\n\n"
            "请分解为子任务（JSON 格式）"
        )

        result = self.run(task_text, context)

        import json
        import re

        # 尝试从返回中提取 JSON
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                tasks = data.get("tasks", [])
                style_notes = data.get("style_notes", style)
                context.style_guide = style_notes
                return tasks, style_notes, context
            except json.JSONDecodeError:
                pass

        # fallback
        return [
            {"type": "visual", "description": f"根据风格'{style}'生成概念图", "priority": 1},
            {"type": "asset", "description": f"创建场景资产: {', '.join(assets)}", "priority": 2},
            {"type": "blueprint", "description": f"实现交互: {', '.join(features)}", "priority": 2},
            {"type": "qa", "description": "检查和优化全流程", "priority": 3},
        ], style, context
