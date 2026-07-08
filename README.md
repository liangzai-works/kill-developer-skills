# kill-developer-skills

> 一个 Codex Meta Skill —— 把"想法 / 需求"端到端变成"可运行软件"的工作流编排器。

## 它是什么

`kill-developer-skills` 不是具体的开发能力，而是一个 **Meta Skill**。它负责：

- **Skill 管理**：根据任务需要检查、安装、激活 Codex Skills。
- **Workflow 编排**：将软件研发过程拆成阶段（Phase / Stage），按 `workflow.yaml` 执行。
- **Artifact 流转**：每个阶段产出可交付物，下一阶段以上一阶段为输入。
- **需求到运行**：从一句话需求或一份完整规格，最终输出可运行、可验证、可截图的软件。

## 设计理念

```
用户输入需求
   │
   ▼
Phase 0  Skill Environment Preparation   ← 检查并安装缺失 Skills
   │
   ▼
Phase 1  Requirement Assessment          ← 区分 Idea Mode / Specification Mode
   │
   ▼
Phase 2  Software Factory Workflow       ← 8 Stages 流水线
   │
   ▼
最终交付（代码 + 运行实例 + 截图 + 报告）
```

## 目录结构

```
kill-developer-skills
├── README.md                            ← 本文件
├── skills/
│   └── software-factory/
│       ├── SKILL.md                     ← Meta Skill 入口
│       ├── workflow.yaml                ← 工作流定义
│       ├── skill-manifest.yaml          ← Skill 依赖清单
│       ├── templates/                   ← 各阶段 Artifact 模板
│       │   ├── PRD.md
│       │   ├── Design.md
│       │   └── Report.md
│       └── prompts/                     ← 各阶段引导式 Prompt
│           ├── requirement.md
│           ├── architecture.md
│           ├── coding.md
│           └── review.md
├── workspace/                           ← 运行时 Artifact 落地目录
│   ├── requirements/
│   ├── design/
│   ├── development/
│   ├── testing/
│   └── delivery/
├── examples/                            ← 示例种子
│   ├── idea-mode/
│   └── spec-mode/
└── docs/                                ← 设计文档 / 教程
```

## 快速开始

1. 把 `skills/software-factory/` 注册到 Codex（个人市场或 `$CODEX_HOME/skills`）。
2. 触发：`$software-factory 开发一个医院索引巡检系统`
3. Meta Skill 会自动：
   - 扫描 `skill-manifest.yaml`，检查依赖。
   - 提示缺失 Skills，确认后安装。
   - 执行 `requirement → design → implement → run → verify → report`。

## 两种输入模式

| 模式 | 触发特征 | 处理策略 |
|------|----------|----------|
| **Idea Mode** | "开发一个 XXX 系统" 类一句话需求 | 主动补全：用户角色 / 功能范围 / 非功能需求 / 数据字典 |
| **Specification Mode** | 已给出功能列表、技术栈、架构 | 不重设计，只做结构化整理 + 缺失内容识别 |

## 支持的扩展方向

- Java Workflow（Spring / JPA）
- Python Workflow（FastAPI / Django）
- Frontend Workflow（React / Vue）
- AIOps Workflow（异常分析 / 巡检）

详细扩展方式见 `docs/extension.md`（预留）。

## License

MIT
