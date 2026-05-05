"""Agent 基类 — ReAct 循环"""
from __future__ import annotations

import json
from typing import Any, Callable

from ue_agent_workflow.llm import LLMClient, ToolCall, LLMResponse
from ue_agent_workflow.context import AgentContext

MAX_ITERATIONS = 15


class ToolSpec:
    """工具描述：自动从函数提取 JSON schema"""
    def __init__(self, fn: Callable, name: str | None = None, description: str | None = None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = description or (fn.__doc__ or "").strip() or self.name
        self._schema: dict | None = None

    @property
    def schema(self) -> dict:
        if self._schema is None:
            import inspect

            sig = inspect.signature(self.fn)
            properties = {}
            required = []

            for pname, param in sig.parameters.items():
                ptype = "string"
                if param.annotation is not inspect.Parameter.empty:
                    type_map = {
                        str: "string",
                        int: "integer",
                        float: "number",
                        bool: "boolean",
                        list: "array",
                        dict: "object",
                    }
                    ptype = type_map.get(param.annotation, "string")

                properties[pname] = {"type": ptype, "description": pname}
                if param.default is inspect.Parameter.empty:
                    required.append(pname)

            self._schema = {
                "name": self.name,
                "description": self.description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
        return self._schema


class BaseAgent:
    """ReAct Agent — 工具调用循环"""
    def __init__(
        self,
        name: str,
        llm: LLMClient,
        system_prompt: str,
        tools: list[ToolSpec] | None = None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools or []

    def _tool_schemas(self) -> list[dict]:
        return [t.schema for t in self.tools]

    def _execute_tool(self, tc: ToolCall, context: AgentContext) -> str:
        for tool in self.tools:
            if tool.name == tc.name:
                try:
                    result = tool.fn(**tc.arguments, context=context)
                    return json.dumps(result, ensure_ascii=False, default=str)
                except Exception as e:
                    return json.dumps({"error": str(e)})
        return json.dumps({"error": f"未知工具: {tc.name}"})

    def run(self, task: str, context: AgentContext | None = None) -> str:
        if context is None:
            context = AgentContext()

        messages = [{"role": "user", "content": task}]
        if context.conversation_history:
            messages = context.conversation_history + messages

        for iteration in range(MAX_ITERATIONS):
            resp = self.llm.chat(
                messages=messages,
                system=self.system_prompt,
                tools=self._tool_schemas() if self.tools else None,
            )

            if resp.tool_calls:
                # 追加 assistant 消息
                assistant_msg: dict = {"role": "assistant", "content": resp.content or ""}
                if resp.tool_calls:
                    assistant_msg["tool_calls"] = [
                        {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}}
                        for tc in resp.tool_calls
                    ]

                # 追加工具结果
                for tc in resp.tool_calls:
                    result = self._execute_tool(tc, context)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

                messages.append(assistant_msg)

            else:
                return resp.content

        return f"[达到最大迭代次数 {MAX_ITERATIONS}] 部分结果: {resp.content if 'resp' in dir() else '无输出'}"
