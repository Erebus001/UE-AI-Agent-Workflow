"""Agent 循环测试"""
import pytest


class TestBaseAgent:
    def test_agent_creation(self, mock_llm):
        from ue_agent_workflow.agent_base import BaseAgent
        agent = BaseAgent("TestAgent", mock_llm, "你是一个测试 Agent")
        assert agent.name == "TestAgent"

    def test_agent_run_basic(self, mock_llm):
        from ue_agent_workflow.agent_base import BaseAgent
        agent = BaseAgent("TestAgent", mock_llm, "测试提示")
        result = agent.run("测试任务")
        assert isinstance(result, str)

    def test_tool_spec_auto_schema(self):
        from ue_agent_workflow.agent_base import ToolSpec

        def sample_tool(name: str, count: int = 1):
            """示例工具"""
            return {"name": name, "count": count}

        spec = ToolSpec(sample_tool)
        schema = spec.schema
        assert schema["name"] == "sample_tool"
        assert "name" in schema["input_schema"]["required"]
        assert "count" not in schema["input_schema"]["required"]
