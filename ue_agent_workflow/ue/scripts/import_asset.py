"""UE Python 脚本模板 — 资产导入"""
# 此脚本由 ue-agent-workflow 自动生成
# 请在 UE Editor 中运行: 菜单 Window → Developer Tools → Python Console
# 然后将此文件拖入控制台，或执行: run import_asset.py

import unreal

asset_tool = unreal.AssetToolsHelpers.get_asset_tools()

# 导入资产
task = unreal.AssetImportTask()
task.filename = "{{source_path}}"
task.destination_path = "/Game/{{destination}}"
task.save = True

asset_tool.import_asset_tasks([task])
print(f"✅ 资产已导入: {{destination}}")
