"""UE Python 脚本模板 — 蓝图创建"""
# 此脚本由 ue-agent-workflow 自动生成
# 请在 UE Editor 中运行

import unreal

factory = unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.{{parent_class}})

asset_tool = unreal.AssetToolsHelpers.get_asset_tools()
bp = asset_tool.create_asset("{{blueprint_name}}", "/Game/Blueprints", None, factory)

if bp:
    print(f"✅ Blueprint 已创建: {{blueprint_name}}")
else:
    print(f"❌ 创建失败: {{blueprint_name}}")
