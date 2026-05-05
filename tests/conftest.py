"""pytest 共用 fixtures"""
import pytest


@pytest.fixture
def mock_config():
    from ue_agent_workflow.config import Config
    return Config(
        llm_provider="openai",
        openai_api_key="test-key",
        openai_base_url="https://api.openai.com/v1",
        log_level="DEBUG",
    )


@pytest.fixture
def mock_llm(mocker):
    """返回一个 mock LLM 客户端"""
    from ue_agent_workflow.llm import LLMResponse

    class MockLLM:
        def __init__(self):
            self.call_count = 0
            self.responses = []

        def chat(self, messages, system=None, tools=None):
            self.call_count += 1
            if self.responses:
                return self.responses.pop(0)
            return LLMResponse(content='{"tasks": [{"type": "visual", "description": "test", "priority": 1}]}')

        def count_tokens(self, messages):
            return 100

    return MockLLM()
