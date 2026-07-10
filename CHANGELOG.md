# CHANGELOG

## v0.5.1 — Heading 双重编号一刀切 + 业务模块强约束

修复了两条用户长期反馈的硬骨头:

### 1. 详细设计 .docx 标题双重编号 bug (彻底修)
**症状**: 模板 `styles.xml` 把 Heading 1/2/3 绑到 `numbering.xml` 的某个 `numId`, 9 节骨架又手写 "一." "1.1", Word 渲染成 "1 文档说明 / 1.1 1.1 内容概要".
**修复**:
- 新增 `scripts/fix_docx_headings.py` (~6.7KB, 仅依赖 python-docx): 强制把 Heading 1/2/3 段落的 `numId=0` (禁用 Word 自动编号), 防御性清理文本残留的 "1. " / "1.1 " 前缀, in-place 保存.
- `templates/02_详细设计文档_九节骨架.md` 改: 不再手写 "一./1.1", 改纯文字 "## 文档说明", 由 Word 自动渲染.
- `prompts/architecture.md` Step 1.5 从"软建议"改为"**强制调 fix_docx_headings.py**".
- `SKILL.md` 搂5.2 重写, 强调"不调脚本不准交付 .docx".

### 2. 架构图 / 模块划分必须按业务模块 (v0.3.0 用户提的硬骨头)
**症状**: agent 跑 demo 时按 SpringBoot 技术分层画架构图 (接入层/应用层/服务层/数据层/基础设施), 业务人员看不懂.
**修复**:
- `templates/03_架构设计.md` 全文重写, 加入"业务模块维度"骨架 + 反例清单 (明确禁止 SpringBoot 分层命名).
- `prompts/architecture.md` Step 2 加业务模块强约束 + 反例清单, 业务模块表格必须含"问题描述 / 职责 / 入口 / 依赖"列.
- `prompts/architecture.md` Step 2.0 调用示例由"5 层技术分层"改为"5 个业务模块示例".
- `scripts/render_arch.py` 默认 fallback 由"接入层/应用层/服务层/数据层/基础设施"改为业务模块示例, 并增加"占位提示"提醒 agent 用真实业务模块重画.
- `SKILL.md` 搂5.3 顶部加"业务模块维度强制 + 反例清单".
- `workflow.yaml` `architecture_diagram.layer_naming_policy.enforce: business_modules`, 加 `forbidden_examples` 与 `required_columns_in_arch_md`.

### 行为变化
- **Stage 2 (详细设计)**: docx skill 生成 `02_<项目名>_详细设计文档.docx` **之后**, **必须**调 `scripts/fix_docx_headings.py`, exit_code 必须为 0, 否则 stage 失败 (`on_failure: stop_workflow`).
- **Stage 3 (架构设计)**: `03_<项目名>_架构设计.md` 必须含"业务模块"表格, 反例命名校验 (assert not 接入层+应用层+服务层+数据层+基础设施层 in arch_layers).
- **Phase 1 (需求评估)**: `01_<项目名>_需求规格说明书.md` 必须含"业务模块清单" (>= 2 项).

### 文件清单
| 文件 | 变化 |
|------|------|
| `scripts/fix_docx_headings.py` | 新增 (~6.7KB) |
| `templates/02_详细设计文档_九节骨架.md` | 重写 (去手写编号) |
| `templates/03_架构设计.md` | 重写 (业务模块维度) |
| `prompts/architecture.md` | 重写 (Step 1.5 / Step 2 强约束) |
| `scripts/render_arch.py` | 修改 default fallback |
| `SKILL.md` | 搂5.2/5.3 + changelog v0.5.1 |
| `workflow.yaml` | version v0.5.0 → v0.5.1; 新增 heading_fix + layer_naming_policy |
| `CHANGELOG.md` | 顶部加 v0.5.1 |

### 反馈来源
- v0.3.0: "模块划分怎么是 SpringBoot 的结构分层? 不应该是实际的业务模块吗"
- v0.4.0: "根据 word 模板生成的新文件的 head 节点前面多了数字 (1 1 文档说明 / 1.1 1.1 内容概要)"

v0.5.1 把这两条做成"脚本兜底 + 反例清单 + workflow assert"三道防线, 不再依赖 agent 自己按 prompt 行事.

### 兼容
v0.5.0 已装 skill 需 reinstall (`scripts/fix_docx_headings.py` 是新文件). 历史产出的 .docx 可补跑 `fix_docx_headings.py` 修复.

---
# CHANGELOG

## v0.5.0 — 架构图自动生成 (内置能力)

- 新增脚本: `skills/software-factory/scripts/render_arch.py`
  - 后端: matplotlib 3.7+, 离线运行, 无网络依赖
  - 输入: `.md` 表格 / `.md` 标题列表 / `--layers=` JSON
  - 输出: PNG (默认 dpi=150, 5 层经典配色, 层间箭头)
  - 中文字体 fallback: SimHei → Microsoft YaHei → PingFang SC → Arial Unicode MS → DejaVu Sans
  - 自带 `--check` 自检入口
- 文档升级:
  - `SKILL.md` frontmatter version 0.4.1 → 0.5.0
  - `SKILL.md` description 增补"内置 render_arch.py 一键生成架构图"
  - `SKILL.md` 搂5.3 文档化架构图生成 (调用方式 / 特性 / 何时调用 / fallback 规则)
  - `SKILL.md` 搂10 changelog 加 v0.5.0
  - `workflow.yaml` version v0.3.0 → v0.5.0
  - `workflow.yaml` 新增 `architecture_diagram:` 块
  - `workflow.yaml` Stage 2 输入增 `03_<项目名>_架构图.png`
  - `workflow.yaml` Stage 3 输出增 `03_<项目名>_架构图.png`, 步骤化生成
  - `prompts/architecture.md` 新增 Step 2.0 "架构图自动生成"
  - `prompts/architecture.md` 「不允许做的事」增 3 条 render_arch.py 强制规则
- 行为变化:
  - Stage 3 改为: 写 md → 调 render_arch.py → verify size>50KB
  - Stage 2 详细设计文档必须嵌入 `03_<项目名>_架构图.png` (在"2. 总体设计"段)
  - 不再允许手画 / ASCII 凑数架构图 (除非 render_arch.py 工具链缺失)
- 兼容: v0.4.x 已装 skill 需 reinstall, 带上 `scripts/render_arch.py`

## v0.4.2 — 模板查找路径文档化

- 新增 `WHERE_TEMPLATE.md` 解释本地 skill 找模板的 4 级优先级
- SKILL.md / coding.md 去掉 CEC 引用 (公网分发清理)
- examples 真实项目名 → 通用示例
- README.md / docs/usage.md 触发示例同步替换
- 模板文件 (.docx) 仍在 .gitignore, 用户私有资产
## v0.1.0 — 初始骨架

- Meta Skill：`software-factory`
- Phase 0（Skill 环境准备）/ Phase 1（需求评估）/ Phase 2（8 Stage 流水线）
- 工作流：`workflow.yaml`
- Skill 清单：`skill-manifest.yaml`
- 模板：`templates/PRD.md` / `Design.md` / `Report.md`
- Prompt：`prompts/requirement.md` / `architecture.md` / `coding.md` / `review.md`
- Workspace：5 个分区（requirements / design / development / testing / delivery）
- 示例种子：idea-mode / spec-mode
- 文档：usage / extension / architecture-decisions
