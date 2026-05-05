"""编排引擎测试"""
import pytest


class TestOrchestrator:
    def test_project_brief_creation(self):
        from ue_agent_workflow.orchestrator import ProjectBrief
        brief = ProjectBrief(
            title="测试项目",
            style="赛博朋克",
            scenario_desc="测试场景",
            assets=["资产1"],
            interactive_features=["功能1"],
        )
        assert brief.title == "测试项目"
        assert brief.assets == ["资产1"]

    def test_orchestrator_requires_config(self, mock_config):
        from ue_agent_workflow.orchestrator import Orchestrator
        orch = Orchestrator(mock_config)
        assert orch is not None
        assert orch.requirement.name == "需求理解Agent"
        assert orch.design.name == "设计Agent"
        assert orch.tech.name == "技术Agent"
        assert orch.qa.name == "质检Agent"

    def test_workflow_result_to_dict(self):
        from ue_agent_workflow.orchestrator import WorkflowResult, ProjectBrief
        brief = ProjectBrief(title="T", style="S", scenario_desc="D")
        result = WorkflowResult(brief=brief)
        d = result.to_dict()
        assert d["project"] == "T"
        assert d["style"] == "S"
