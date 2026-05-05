"""CLI 入口 — Click 命令"""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from ue_agent_workflow.__init__ import __version__
from ue_agent_workflow.config import Config
from ue_agent_workflow.orchestrator import Orchestrator, ProjectBrief

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """UE Agent Workflow — AI Agent 驱动的 Unreal Engine 创作工作流"""


@main.command()
@click.option("--title", required=True, help="项目标题")
@click.option("--style", required=True, help="视觉风格描述")
@click.option("--desc", required=True, help="场景描述")
@click.option("--assets", default="", help="所需资产列表，逗号分隔")
@click.option("--features", default="", help="交互功能，逗号分隔")
@click.option("--provider", default=None, help="LLM 提供商 (claude/mimo/openai)")
def run_brief(title, style, desc, assets, features, provider):
    """从命令行参数运行完整工作流"""
    config = Config.load()
    if provider:
        config.llm_provider = provider

    missing = config.missing_keys()
    if missing:
        console.print(f"[red]❌ 缺少 API Key: {', '.join(missing)}[/red]")
        console.print("运行 [bold]ue-agent-workflow init-config[/bold] 配置")
        sys.exit(1)

    brief = ProjectBrief(
        title=title,
        style=style,
        scenario_desc=desc,
        assets=[a.strip() for a in assets.split(",") if a.strip()],
        interactive_features=[f.strip() for f in features.split(",") if f.strip()],
    )

    console.print(Panel.fit(
        f"[bold cyan]项目:[/bold cyan] {brief.title}\n"
        f"[bold cyan]风格:[/bold cyan] {brief.style}\n"
        f"[bold cyan]场景:[/bold cyan] {brief.scenario_desc}\n"
        f"[bold cyan]资产:[/bold cyan] {', '.join(brief.assets) or '无'}\n"
        f"[bold cyan]交互:[/bold cyan] {', '.join(brief.interactive_features) or '无'}",
        title="🚀 启动工作流",
    ))

    orchestrator = Orchestrator(config)
    result = orchestrator.run(brief)

    # 显示结果摘要
    console.print("\n[green]✅ 工作流完成[/green]\n")

    table = Table(title="结果摘要")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="white")
    table.add_row("标题", result.brief.title)
    table.add_row("风格", result.style_notes or result.brief.style)
    table.add_row("子任务数", str(len(result.tasks)))
    table.add_row("生成文件", str(len(result.generated_files)))
    console.print(table)

    if result.generated_files:
        console.print("\n[bold]生成的文件:[/bold]")
        for fp in result.generated_files:
            console.print(f"  📄 {fp}")


@main.command()
@click.argument("brief_file", type=click.Path(exists=True))
def run_file(brief_file):
    """从 JSON 文件加载项目需求并运行"""
    import json
    data = json.loads(Path(brief_file).read_text(encoding="utf-8"))
    brief = ProjectBrief(**data)
    config = Config.load()

    missing = config.missing_keys()
    if missing:
        console.print(f"[red]❌ 缺少 API Key: {', '.join(missing)}[/red]")
        sys.exit(1)

    orchestrator = Orchestrator(config)
    orchestrator.run(brief)


@main.command()
def init_config():
    """初始化配置文件（创建 .env）"""
    env_path = Path(".env")
    if env_path.exists():
        console.print("[yellow].env 文件已存在[/yellow]")
        if not click.confirm("覆盖?"):
            return

    example = Path(".env.example")
    if not example.exists():
        console.print("[red]❌ 找不到 .env.example[/red]")
        return

    env_path.write_text(example.read_text())
    console.print("[green]✅ .env 已创建，请编辑填入 API Key[/green]")
    console.print("运行 [bold]ue-agent-workflow run-brief ...[/bold] 开始使用")


@main.command()
def agents():
    """列出所有可用 Agent"""
    table = Table(title="可用 Agent")
    table.add_column("Agent", style="cyan")
    table.add_column("职责", style="white")
    table.add_row("需求理解Agent", "解析项目需求，拆解为子任务")
    table.add_row("设计Agent", "生成视觉概念、材质和 UI 方案")
    table.add_row("技术Agent", "规划 UE 资产导入和蓝图逻辑")
    table.add_row("质检Agent", "检查风格一致性和技术完整性")
    console.print(table)


@main.command()
def version():
    """显示版本信息"""
    console.print(f"ue-agent-workflow v{__version__}")


if __name__ == "__main__":
    main()
