# UE-Agent-Workflow

基于 AI Agent 的 Unreal Engine 数字媒体综合创作工作流。

## 快速开始

```bash
# 安装
pip install -e .

# 配置 API Key
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 运行
ue-agent-workflow run-brief --title "赛博朋克城市" --style "霓虹美学" --desc "可交互夜景" --assets "建筑,灯光" --features "漫游,点击"
```

## 架构

```
CLI 命令
   │
 Orchestrator ─── 编排 4 个 Agent
   │
   ├─ 需求理解Agent → 拆解子任务
   ├─ 设计Agent     → 视觉概念/材质/UI
   ├─ 技术Agent     → UE 资产/蓝图
   └─ 质检Agent     → 风格检查/性能评审
   │
 LLM Client ─── 统一接口，支持 Claude / MiMo
 UE Bridge  ─── 直连 UE / 文件脚本 / Null 降级
```

## LLM 支持

| Provider | 配置 | 说明 |
|----------|------|------|
| Claude | `LLM_PROVIDER=claude` + `CLAUDE_API_KEY` | 推荐，需安装 anthropic |
| MiMo | `LLM_PROVIDER=mimo` + `MIMO_API_KEY` | 小米 MiMo API |
| OpenAI | `LLM_PROVIDER=openai` + `OPENAI_API_KEY` | 通用 OpenAI 兼容 |

## UE 集成

三种模式自动切换：
- **直连模式**：在 UE Editor Python 环境中直接使用 `import unreal`
- **文件模式**：生成 .py 脚本到 UE 项目 `Content/Python/` 目录
- **Null 模式**：无 UE 时打印操作说明，其余功能全部正常

**不需要 UE 也能使用 90% 的功能。**

## 项目结构

```
ue_agent_workflow/
├── llm.py            # 统一 LLM 接口
├── agent_base.py     # ReAct Agent 循环
├── context.py        # Agent 间共享上下文
├── tools.py          # 工具函数
├── orchestrator.py   # 多 Agent 编排
├── cli.py            # CLI 入口
├── agents/           # Agent 实现
│   ├── requirement.py
│   ├── design.py
│   ├── tech.py
│   └── qa.py
└── ue/               # UE 桥接
    ├── bridge.py     # 三种桥接模式
    └── scripts/      # UE 脚本模板
```

## 命令

```bash
ue-agent-workflow run-brief   # 从参数运行
ue-agent-workflow run-file    # 从 JSON 运行
ue-agent-workflow init-config # 初始化配置
ue-agent-workflow agents      # 查看 Agent 列表
ue-agent-workflow version     # 版本信息
```
