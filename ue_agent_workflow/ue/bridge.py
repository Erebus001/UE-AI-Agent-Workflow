"""Unreal Engine 桥接 — 支持直连/文件/null 三种模式"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ue_agent_workflow.config import Config


class UEBridge(ABC):
    @abstractmethod
    def exec_script(self, script_content: str, name: str = "script") -> dict:
        ...

    @abstractmethod
    def import_asset(self, asset_name: str, source_path: str) -> dict:
        ...

    @abstractmethod
    def create_blueprint(self, name: str, parent_class: str = "Actor") -> dict:
        ...

    @abstractmethod
    def run_command(self, cmd: str) -> dict:
        ...


class DirectBridge(UEBridge):
    """直连模式：在 UE Python 环境中运行"""
    def __init__(self):
        try:
            import unreal  # noqa
        except ImportError:
            raise RuntimeError("DirectBridge 只能在 Unreal Editor Python 环境中使用")
        self.unreal = unreal

    def exec_script(self, script_content: str, name: str = "script") -> dict:
        try:
            exec(script_content)
            return {"status": "ok", "output": f"脚本 [{name}] 执行成功"}
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def import_asset(self, asset_name: str, source_path: str) -> dict:
        try:
            task = self.unreal.AssetImportTask()
            task.filename = source_path
            task.destination_path = f"/Game/{asset_name}"
            task.save = True
            self.unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            return {"status": "ok", "asset": asset_name}
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def create_blueprint(self, name: str, parent_class: str = "Actor") -> dict:
        try:
            factory = self.unreal.BlueprintFactory()
            parent_cls = getattr(self.unreal, parent_class, self.unreal.Actor)
            factory.set_editor_property("ParentClass", parent_cls)
            tools = self.unreal.AssetToolsHelpers.get_asset_tools()
            tools.create_asset(name, "/Game/Blueprints", None, factory)
            return {"status": "ok", "name": name}
        except Exception as e:
            return {"status": "error", "output": str(e)}

    def run_command(self, cmd: str) -> dict:
        return {"status": "ok", "note": f"DirectBridge: {cmd}"}


class FileBridge(UEBridge):
    """文件模式：生成 .py 脚本到 UE 项目目录"""
    def __init__(self, ue_project_path: str):
        self.script_dir = Path(ue_project_path) / "Content" / "Python"
        self.script_dir.mkdir(parents=True, exist_ok=True)

    def exec_script(self, script_content: str, name: str = "script") -> dict:
        path = self.script_dir / f"{name}.py"
        path.write_text(script_content, encoding="utf-8")
        return {
            "status": "file_created",
            "path": str(path),
            "note": f"请在 UE Editor 中打开 Python 控制台，执行: run {path.name}",
        }

    def import_asset(self, asset_name: str, source_path: str) -> dict:
        script = f"""# Auto-generated import for: {asset_name}
import unreal
task = unreal.AssetImportTask()
task.filename = r"{source_path}"
task.destination_path = "/Game/{asset_name}"
task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
print(f"Imported: {asset_name}")
"""
        return self.exec_script(script, f"import_{asset_name}")

    def create_blueprint(self, name: str, parent_class: str = "Actor") -> dict:
        script = f"""# Auto-generated Blueprint: {name}
import unreal
factory = unreal.BlueprintFactory()
factory.set_editor_property("ParentClass", unreal.{parent_class})
tools = unreal.AssetToolsHelpers.get_asset_tools()
bp = tools.create_asset("{name}", "/Game/Blueprints", None, factory)
print(f"Blueprint created: {name}")
"""
        return self.exec_script(script, f"BP_{name}")

    def run_command(self, cmd: str) -> dict:
        return self.exec_script(f"# Command: {cmd}\nprint('{cmd}')", "command")


class NullBridge(UEBridge):
    """空模式：无 UE 可用时降级"""
    def exec_script(self, script_content: str, name: str = "script") -> dict:
        return {
            "status": "skipped",
            "note": f"[UE 未连接] 脚本 [{name}] 已准备，请在 UE Editor Python 控制台中运行。",
            "script_preview": script_content[:200],
        }

    def import_asset(self, asset_name: str, source_path: str) -> dict:
        return self.exec_script(
            f"# import asset: {asset_name} from {source_path}",
            f"import_{asset_name}",
        )

    def create_blueprint(self, name: str, parent_class: str = "Actor") -> dict:
        return self.exec_script(
            f"# create Blueprint: {name} ({parent_class})",
            f"BP_{name}",
        )

    def run_command(self, cmd: str) -> dict:
        return {"status": "skipped", "note": f"[UE 未连接] 命令已记录: {cmd}"}


def create_bridge(config: Config) -> UEBridge:
    """自动检测并创建合适的 UE 桥接"""
    try:
        import unreal  # noqa
        return DirectBridge()
    except ImportError:
        pass

    if config.ue_project_path and Path(config.ue_project_path).exists():
        return FileBridge(config.ue_project_path)

    return NullBridge()
