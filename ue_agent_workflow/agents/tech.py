"""技术 Agent — UE 资产导入、蓝图、实现"""
from ue_agent_workflow.agent_base import BaseAgent, ToolSpec
from ue_agent_workflow.context import AgentContext
from ue_agent_workflow.llm import LLMClient
from ue_agent_workflow.tools import ue_import_asset, ue_create_blueprint, write_file, read_file, generate_concept

TECH_SYSTEM_PROMPT = """你是一个 Unreal Engine 技术美术师。
你的职责：
- 规划资产导入 UE 的流程
- 编写 Blueprint 蓝图逻辑描述
- 处理光照、材质、性能优化
- 为非在 UE 环境中的操作提供可执行的脚本

可用工具：
- ue_import_asset: 生成资产导入脚本
- ue_create_blueprint: 生成蓝图创建脚本
- write_file: 保存技术文档和脚本
- read_file: 读取已有文件
"""


class TechAgent(BaseAgent):
    def __init__(self, llm: LLMClient):
        tools = [
            ToolSpec(ue_import_asset, "ue_import_asset", "生成 UE 资产导入脚本"),
            ToolSpec(ue_create_blueprint, "ue_create_blueprint", "生成 UE 蓝图创建脚本"),
            ToolSpec(write_file, "write_file", "保存文件到 output 目录"),
            ToolSpec(read_file, "read_file", "读取文件内容"),
        ]
        super().__init__("技术Agent", llm, TECH_SYSTEM_PROMPT, tools)

    def process(self, task_desc: str, context: AgentContext) -> str:
        prompt = f"当前项目风格: {context.style_guide}\n已有概念图: {len(context.generated_concepts)} 张\n\n任务: {task_desc}\n\n注意：如果无法直接操作 UE，请生成可以在 UE Editor Python 控制台中运行的 .py 脚本。"
        return self.run(prompt, context)
