"""质检 Agent — 风格一致性、性能检查"""
from ue_agent_workflow.agent_base import BaseAgent, ToolSpec
from ue_agent_workflow.context import AgentContext
from ue_agent_workflow.llm import LLMClient
from ue_agent_workflow.tools import read_file

QA_SYSTEM_PROMPT = """你是一个 Unreal Engine 项目质量评审员。
你的职责：
1. 检查所有生成的资产和脚本是否符合项目风格要求
2. 检查蓝图逻辑的完整性
3. 给出优化建议和评审报告

可用工具：
- read_file: 读取生成的文件进行检查
"""


class QAAgent(BaseAgent):
    def __init__(self, llm: LLMClient):
        tools = [
            ToolSpec(read_file, "read_file", "读取文件内容"),
        ]
        super().__init__("质检Agent", llm, QA_SYSTEM_PROMPT, tools)

    def process(self, context: AgentContext) -> str:
        summary = context.to_summary()
        prompt = f"""请对以下项目进行质量评审:

{summary}

输出格式:
1. 风格一致性: [pass/fail] + 说明
2. 技术完整性: [pass/fail] + 说明
3. 优化建议: 列出 2-3 条建议
4. 总体评分: A/B/C/D
"""
        return self.run(prompt, context)
