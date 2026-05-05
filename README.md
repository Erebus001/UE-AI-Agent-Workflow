# UE-Agent-Workflow

基于 AI Agent 的 Unreal Engine 数字媒体综合创作工作流

## 项目概述

利用多 Agent 协作系统，打通从概念设计到 Unreal Engine 交互场景落地的全流程。Agent 自动解析需求、生成视觉资产、编写蓝图逻辑，大幅缩短数字媒体创作周期。

## 核心架构

```
用户需求 → 需求理解 Agent → 拆解任务
                              ├── 设计 Agent（概念图 / 材质 / UI）
                              ├── 技术 Agent（资产导入 / 蓝图 / 光照）
                              └── 质检 Agent（风格一致性 / 性能检查）
                                    ↓
                            UE 可交互场景
```

## Agent 分工

| Agent | 职责 |
|-------|------|
| **需求理解 Agent** | 解析项目 brief，拆解为视觉、资产、蓝图子任务 |
| **设计 Agent** | 根据风格参考生成概念图、材质贴图和 UI 图标 |
| **技术 Agent** | 资产导入 UE、编写蓝图逻辑、光照烘焙与性能优化 |
| **质检 Agent** | 检查跨节点风格一致性和引擎内性能指标 |

## 技术栈

- **LLM**: Claude / MiMo 系列模型
- **Agent 框架**: Python 多 Agent 编排
- **引擎**: Unreal Engine 5.x
- **资产管线**: Blender / Substance Painter 自动化
