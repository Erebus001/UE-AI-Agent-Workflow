"""LLM 接口测试"""
import pytest


class TestLLMClient:
    def test_create_openai_client(self, mock_config):
        from ue_agent_workflow.llm import create_llm
        client = create_llm(mock_config)
        assert client is not None

    def test_openai_client_requires_key(self):
        from ue_agent_workflow.config import Config
        from ue_agent_workflow.llm import create_llm
        cfg = Config(llm_provider="openai", openai_api_key="")
        with pytest.raises(ValueError, match="OpenAI"):
            create_llm(cfg)

    def test_claude_client_requires_key(self):
        from ue_agent_workflow.config import Config
        from ue_agent_workflow.llm import create_llm
        cfg = Config(llm_provider="claude", claude_api_key="")
        with pytest.raises(ValueError, match="Claude"):
            create_llm(cfg)

    def test_unknown_provider(self):
        from ue_agent_workflow.config import Config
        from ue_agent_workflow.llm import create_llm
        cfg = Config(llm_provider="unknown")
        with pytest.raises(ValueError, match="不支持"):
            create_llm(cfg)
