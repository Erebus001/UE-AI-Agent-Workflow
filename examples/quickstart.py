"""快速开始示例"""
from ue_agent_workflow.config import Config
from ue_agent_workflow.orchestrator import Orchestrator, ProjectBrief

# 1. 加载配置（会读取 .env 文件）
config = Config.load()

# 2. 检查 API Key
missing = config.missing_keys()
if missing:
    print(f"❌ 缺少 API Key: {', '.join(missing)}")
    print("请先创建 .env 文件，参考 .env.example")
    exit(1)

# 3. 创建项目需求
brief = ProjectBrief(
    title="赛博朋克城市夜景",
    style="赛博朋克+霓虹美学，高饱和度对比",
    scenario_desc="一个可漫游的赛博朋克风格城市夜景场景",
    assets=["建筑模型", "霓虹灯材质", "路面贴图"],
    interactive_features=["角色漫游控制", "点击交互"],
)

# 4. 启动工作流
orchestrator = Orchestrator(config)
result = orchestrator.run(brief)

# 5. 查看结果
print(f"\n✅ 完成! 生成 {len(result.generated_files)} 个文件")
