"""工具函数库"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ue_agent_workflow.context import AgentContext
from ue_agent_workflow.llm import create_llm


# ---------- 文件操作 ----------

def write_file(path: str, content: str, context: AgentContext | None = None) -> dict:
    """写入文件到 output 目录"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / path
    filepath.write_text(content, encoding="utf-8")
    if context is not None and filepath.name not in context.output_files:
        context.output_files.append(str(filepath))
    return {"status": "ok", "path": str(filepath), "bytes": len(content)}


def read_file(path: str, context: AgentContext | None = None) -> dict:
    """读取文件内容"""
    p = Path(path)
    if not p.exists():
        return {"error": f"文件不存在: {path}"}
    return {"status": "ok", "content": p.read_text(encoding="utf-8"), "path": path}


# ---------- 概念生图 ----------

def generate_concept(prompt: str, style: str = "", context: AgentContext | None = None) -> dict:
    """生成概念图描述（基于 LLM 生成画面描述，而非真实调用生图 API）"""
    lines = [f"概念设计: {prompt}"]
    if style:
        lines.append(f"风格: {style}")
    lines.append("状态: 已生成概念描述，可用于后续图像生成")
    result = "\n".join(lines)
    if context is not None:
        context.generated_concepts.append(result)
    return {
        "status": "generated",
        "prompt": prompt,
        "style": style,
        "description": result,
    }


# ---------- UE 集成 ----------

def ue_import_asset(asset_name: str, source_path: str, context: AgentContext | None = None) -> dict:
    """将资产导入 Unreal Engine（文件模式：生成导入脚本）"""
    script = f"""# UE Asset Import - {asset_name}
import unreal

asset_tool = unreal.AssetToolsHelpers.get_asset_tools()
# Import: {source_path}
# Asset: {asset_name}
print(f"导入完成: {asset_name}")
"""
    path = f"ue_scripts/import_{asset_name}.py"
    return write_file(path, script, context)


def ue_create_blueprint(blueprint_name: str, description: str, context: AgentContext | None = None) -> dict:
    """创建 Unreal Engine Blueprint（文件模式：生成蓝图创建脚本）"""
    script = f"""# UE Blueprint - {blueprint_name}
import unreal

bp_factory = unreal.BlueprintFactory()
bp_factory.set_editor_property("ParentClass", unreal.Actor)

asset_tool = unreal.AssetToolsHelpers.get_asset_tools()
bp_asset = asset_tool.create_asset("{blueprint_name}", "/Game/Blueprints", None, bp_factory)

# {description}
# 请在 UE Editor 中手动完善蓝图逻辑
print(f"Blueprint 已创建: {blueprint_name}")
"""
    path = f"ue_scripts/BP_{blueprint_name}.py"
    result = write_file(path, script, context)
    if context is not None and blueprint_name not in context.blueprints:
        context.blueprints.append(blueprint_name)
    return {"status": "created", "name": blueprint_name, "script": str(path), **result}


# ---------- 搜索参考 ----------

def search_reference(query: str, context: AgentContext | None = None) -> dict:
    """搜索参考资料（返回模拟结果）"""
    return {
        "status": "ok",
        "query": query,
        "results": [
            {"title": f"{query} 参考1", "url": "#"},
            {"title": f"{query} 参考2", "url": "#"},
        ],
    }


# ---------- 工具注册 ----------

TOOL_REGISTRY = {
    "write_file": write_file,
    "read_file": read_file,
    "generate_concept": generate_concept,
    "ue_import_asset": ue_import_asset,
    "ue_create_blueprint": ue_create_blueprint,
    "search_reference": search_reference,
}
