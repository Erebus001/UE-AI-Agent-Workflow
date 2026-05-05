"""统一 LLM 接口 — 支持 Claude / MiMo / OpenAI-compatible"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ue_agent_workflow.config import Config


# ---------- 数据结构 ----------

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str = ""
    tool_calls: list[ToolCall] | None = None
    usage: dict | None = None
    stop_reason: str = ""


# ---------- 抽象基类 ----------

class LLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        ...

    @abstractmethod
    def count_tokens(self, messages: list[dict]) -> int:
        ...


# ---------- Claude 实现 ----------

class ClaudeClient(LLMClient):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250506"):
        try:
            import anthropic
        except ImportError:
            raise ImportError("请先安装 anthropic: pip install anthropic")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        kwargs = dict(model=self.model, max_tokens=4096)
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        # 转换 messages 格式: 移除 system 消息 (Claude 用单独参数)
        msgs = [m for m in messages if m.get("role") != "system"]
        kwargs["messages"] = msgs

        resp = self.client.messages.create(**kwargs)

        content = ""
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input if isinstance(block.input, dict) else json.loads(block.input),
                ))

        return LLMResponse(
            content=content,
            tool_calls=tool_calls or None,
            usage={"input": resp.usage.input_tokens, "output": resp.usage.output_tokens},
            stop_reason=resp.stop_reason or "",
        )

    def count_tokens(self, messages: list[dict]) -> int:
        try:
            resp = self.client.beta.messages.count_tokens(model=self.model, messages=messages)
            return resp.input_tokens
        except Exception:
            return 0


# ---------- OpenAI-compatible 实现 (涵盖 MiMo) ----------

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, base_url: str | None = None, model: str = "gpt-4o"):
        try:
            import openai
        except ImportError:
            raise ImportError("请先安装 openai: pip install openai")

        kwargs = dict(api_key=api_key)
        if base_url:
            kwargs["base_url"] = base_url
        self.client = openai.OpenAI(**kwargs)
        self.model = model

    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        msgs = list(messages)
        if system:
            msgs.insert(0, {"role": "system", "content": system})

        kwargs: dict = dict(model=self.model, messages=msgs)
        if tools:
            kwargs["tools"] = tools

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]

        content = choice.message.content or ""
        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(
            content=content,
            tool_calls=tool_calls or None,
            usage={"input": resp.usage.prompt_tokens, "output": resp.usage.completion_tokens} if resp.usage else None,
            stop_reason=choice.finish_reason or "",
        )

    def count_tokens(self, messages: list[dict]) -> int:
        return 0  # OpenAI SDK 没有简单的方法


# ---------- 工厂函数 ----------

def create_llm(config: Config) -> LLMClient:
    """根据配置创建 LLM 客户端"""
    provider = config.llm_provider.lower()

    if provider == "claude":
        if not config.claude_api_key:
            raise ValueError("使用 Claude 需要设置 CLAUDE_API_KEY")
        return ClaudeClient(api_key=config.claude_api_key, model=config.claude_model)

    elif provider == "mimo":
        if not config.mimo_api_key:
            raise ValueError("使用 MiMo 需要设置 MIMO_API_KEY")
        return OpenAIClient(
            api_key=config.mimo_api_key,
            base_url=config.mimo_base_url or "https://api.xiaomimimo.com/v1",
            model=config.mimo_model,
        )

    elif provider in ("openai", ""):
        if not config.openai_api_key:
            raise ValueError("使用 OpenAI 需要设置 OPENAI_API_KEY")
        return OpenAIClient(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url or None,
            model=config.openai_model if hasattr(config, "openai_model") else "gpt-4o",
        )

    else:
        raise ValueError(f"不支持的 LLM provider: {provider}")
