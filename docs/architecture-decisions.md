# docs/architecture-decisions.md

> 关键设计决策记录（ADR-lite）。

## ADR-001：把 Skill 分层而不是平铺

- **状态**：采纳
- **背景**：把所有 Skills 平铺会让主 Skill 越来越胖。
- **决策**：保留 `software-factory` 作为 Meta Skill，业务能力由其他 Skills 提供。
- **后果**：Meta Skill 永远只有一个入口；新增能力加 manifest + prompt 即可。

## ADR-002：Artifact 走文件，不走会话上下文

- **状态**：采纳
- **背景**：跨 Stage 直传上下文会让"恢复 / 重跑"实现困难。
- **决策**：每个 Stage 写文件到 `workspace/` 指定目录。
- **后果**：可单 Stage 重跑；可归档；可 diff。

## ADR-003：Phase 0 与 Phase 2 严格分离

- **状态**：采纳
- **背景**：见过一些 AI 工具在"装好 Skill 后立即执行"，导致错误静默扩散。
- **决策**：Phase 0 仅做环境准备；必须输出 `phase0-report.md`。
- **后果**：用户可见"装 vs 执行"两段边界，便于排查。

## ADR-004：Idea / Spec Mode 收敛到同一份 PRD 模板

- **状态**：采纳
- **背景**：两套模板会导致下游 Stage 写两套适配。
- **决策**：Mode A 补全字段；Mode B 整理字段；最终都套 `templates/PRD.md`。
- **后果**：下游契约统一。

## ADR-005：Workflow 状态持久化

- **状态**：采纳
- **决策**：用 `workspace/.workflow-state.json` 记录当前 Stage、已产 Artifact、失败信息。
- **后果**：支持 `pause / resume / rerun`。
