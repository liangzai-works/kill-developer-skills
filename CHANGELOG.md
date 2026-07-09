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
