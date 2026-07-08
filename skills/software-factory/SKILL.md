---
name: software-factory
description: |
  Meta Skill —— 软件工厂工作流编排器。把一句话需求或完整规格，通过 Phase 0（Skill 环境准备）
  → Phase 1（需求评估）→ Phase 2（8 Stage 流水线），交付可运行、可截图验证的软件。
  不重复实现具体开发能力；只负责 Skill 管理、阶段编排、Artifact 流转。
version: 0.1.0
type: meta
author: kill-developer-skills
tags:
  - meta-skill
  - workflow
  - software-factory
  - orchestration
---

# software-factory (Meta Skill)

> Skill Manager + Software Factory Workflow

## Metadata

| 字段 | 值 |
|------|----|
| **name** | `software-factory` |
| **type** | `meta` |
| **version** | `0.1.0` |
| **entry** | `SKILL.md` |
| **workflow** | `workflow.yaml` |
| **manifest** | `skill-manifest.yaml` |

## 它做什么

`software-factory` 是个 **Meta Skill**，本身不写代码、不画原型、不做测试。
它编排其他 Skills，让"一句话需求 → 可运行软件"在 Codex 里一条龙跑完。

## 不做什么

- 不重写已有的 Skill 能力（例如不自带 Coding，而是调用 `coding`）。
- 不在 Phase 0 安装完 Skills 后立即执行；必须先验证可用。
- 不破坏用户已有技术决策；只在缺失内容时补全。

## Input

```yaml
user_input:
  text: "用户的原始需求（必填）"
  mode: "auto | idea | spec"     # auto 时根据输入自动判断
  workspace: "./workspace"        # Artifact 输出根目录，默认相对于 skill 目录
  install_mode: "interactive | auto"   # 缺失 Skill 时是否自动装
```

## Execution

整体流程分两段：**Phase 0/1 准备** → **Phase 2 流水线**。

### Phase 0 — Skill Environment Preparation

```
分析需求 → 读 skill-manifest.yaml → 列依赖 → 对比已装 Skills
                                                  │
                            ┌─────────────────────┴─────────────────────┐
                       全部满足                                  存在缺失
                            │                                          │
                            ▼                                          ▼
                     进入 Phase 1                       install_mode = interactive ?
                                                              │           │
                                                              ▼           ▼
                                                       询问用户确认       自动安装
                                                              │           │
                                                              └─────┬─────┘
                                                                    ▼
                                                          安装 → 验证 → 进入 Phase 1
```

执行步骤：

1. 解析 `user_input.text`，识别领域关键词（"医院"/"巡检"/"索引"等）。
2. 读取 `skill-manifest.yaml`，得到每个 Workflow Stage 的 required-skills。
3. 扫描 `$CODEX_HOME/skills`，比对本 Skill 已知清单。
4. 缺失 Skill 集合若非空：
   - `install_mode == "interactive"`：`request_user_input` 询问用户。
   - `install_mode == "auto"`：直接安装并写日志。
5. 对每个新装 Skill，执行最小烟雾测试（读 `SKILL.md` 头部 metadata）。
6. 通过后输出 `phase0-report.md`，进入 Phase 1。

> ⚠️ Phase 0 **绝不**直接执行 Workflow，哪怕 Skills 全部就位。  
> 必须产 `phase0-report.md` 后由主流程决定是否进入 Phase 1。

### Phase 1 — Requirement Assessment

自动识别 Mode，进入对应处理路径：

#### Mode A · Idea Mode

**触发**：用户输入仅含目标 / 业务描述（典型："开发一个 XXX 系统"）。

处理：

1. 调用 `requirement-analysis` Skill（或本地 `prompts/requirement.md`）。
2. 补全维度：
   - 用户角色
   - 功能范围（MVP / V1 / V2）
   - 非功能需求（性能、安全、可观测）
   - 数据字典初步推测
3. 识别显式 / 隐式风险。
4. 输出 `workspace/requirements/requirement-analysis.md`。

#### Mode B · Specification Mode

**触发**：用户输入已含功能列表 / 技术栈 / 数据流程 / 架构图。

处理：

1. 不重设计。读取用户原文，落 `workspace/requirements/raw-input.md`。
2. 调用 `documentation` Skill 做结构化整理 → `PRD.md`。
3. 识别缺失内容（列出 `gap-list.md`）。
4. 保留用户所有技术决策；只在缺失时追问。

> 两个 Mode 最终都产出 `PRD.md`（同一模板），后续 Stage 输入一致。

#### Mode 自动判断规则

```yaml
contains_any(["功能列表","技术栈","API","数据库","类图","时序"], strict=true):
  -> spec
else:
  -> idea
```

### Phase 2 — Software Factory Workflow

按 `workflow.yaml` 定义的 Stage 顺序串行执行。每个 Stage：

```
[读输入 Artifact] → [加载对应 Skill] → [执行] → [产出 Artifact] → [校验] → 进入下一 Stage
```

| Stage | 名称 | 必选 | 主要 Skill | 输入 | 输出 |
|-------|------|------|-----------|------|------|
| 1 | Requirement Specification | ✅ | requirement-analysis, documentation | `requirement-analysis.md` | `PRD.md` / `UserStory.md` / `AcceptanceCriteria.md` |
| 2 | Product Design | ✅ | product-design, prototype | `PRD.md` | `design/prototype/*`, `ui-spec.md` |
| 3 | UI Design | ⬜ | ui-design | `ui-spec.md` | `design-system.md`, `component-spec.md` |
| 4 | Architecture Design | ✅ | architecture-design | `PRD.md`, `UI 规范` | `architecture.md`, `api-spec.md`, `db-schema.md` |
| 5 | Implementation | ✅ | coding | `architecture.md`, `db-schema.md` | `workspace/development/source-code/**` |
| 6 | Build & Run | ✅ | build, deploy | `source-code/**` | 运行实例 + 健康检查日志 |
| 7 | Browser Validation | ✅ | browser-automation, playwright | URL | `screenshots/**`, `validation-report.md` |
| 8 | Testing & Review | ✅ | testing, code-review | `source-code/**`, `screenshots/**` | `test-report.md`, `code-review-report.md` |

> ⬜ 标记的 Stage 可按项目类型跳过（CLI / 后端服务无 UI 时跳过 Stage 3）。

## Output

完成 Phase 2 后产出统一交付包：

```
workspace/
├── requirements/
│   ├── raw-input.md
│   ├── requirement-analysis.md
│   ├── PRD.md
│   └── AcceptanceCriteria.md
├── design/
│   ├── prototype/
│   ├── ui-spec.md
│   └── architecture.md
├── development/
│   └── source-code/         ← 真正的可运行代码
├── testing/
│   ├── test-report.md
│   └── validation-report.md
└── delivery/
    ├── final-report.md      ← 给用户看的总结
    └── screenshots/         ← 浏览器验证截图
```

## Failure Handling

- 任意 Stage 失败：写 `STAGE_FAIL.md`，保留已产 Artifact，**不**自动清理。
- 用户可恢复：输入"恢复 software-factory 从 Stage N 继续"。
- 支持单 Stage 重跑：输入"重跑 Stage 4 architecture"。
- 三次同类失败：把状态标记为 `blocked`，询问用户。

## 触发方式

```text
$software-factory 开发一个医院索引巡检系统
$software-factory --mode=spec 基于 Spring Boot + Vue，详见附件 spec.md
$software-factory --resume
$software-factory --rerun=architecture
```

## 不变的约束

1. 不重复实现已有 Skill 能力。
2. 所有阶段通过 Artifact 传递，禁止跨 Stage 直传上下文。
3. 每个 Stage 可独立运行（输入满足前置 Artifact 即可单跑）。
4. 不锁定技术栈：Java / Python / Frontend / AIOps 都可挂载。
