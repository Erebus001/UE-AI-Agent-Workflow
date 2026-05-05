"""设计 Agent — 视觉概念、材质、UI"""
from ue_agent_workflow.agent_base import BaseAgent, ToolSpec
from ue_agent_workflow.context import AgentContext
from ue_agent_workflow.llm import LLMClient
from ue_agent_workflow.tools import generate_concept, write_file, search_reference

DESIGN_SYSTEM_PROMPT = """你是一个 Unreal Engine 视觉设计师。
你的职责：
- 根据需求生成视觉概念和设计方案
- 输出材质/贴图设计描述
- 确保视觉风格统一

可用工具：
- generate_concept: 生成概念图描述
- write_file: 保存设计文档
- search_reference: 搜索参考素材
"""


class DesignAgent(BaseAgent):
    def __init__(self, llm: LLMClient):
        tools = [
            ToolSpec(generate_concept, "generate_concept", "生成概念视觉设计"),
            ToolSpec(write_file, "write_file", "保存文件到 output 目录"),
            ToolSpec(search_reference, "search_reference", "搜索参考资料"),
        ]
        super().__init__("设计Agent", llm, DESIGN_SYSTEM_PROMPT, tools)

    def process(self, task_desc: str, context: AgentContext) -> str:
        prompt = f"当前项目风格: {context.style_guide}\n\n任务: {task_desc}"
        return self.run(prompt, context)
