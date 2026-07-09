# docs/usage.md

> 怎么用 `kill-developer-skills`。

## 1. 安装到 Codex

把 `skills/software-factory/` 注册进 Codex 任一市场：

```bash
# 方式 A：个人市场（默认）
mkdir -p $CODEX_HOME/marketplaces/personal/.codex-plugin
cp -r skills/software-factory $CODEX_HOME/marketplaces/personal/.codex-plugin/
```

或直接放到 `$CODEX_HOME/skills/software-factory/` 让 Codex 自动发现。

## 2. 触发方式

```text
$software-factory 开发一个运维巡检系统
$software-factory --mode=spec
$software-factory --dry-run
$software-factory --resume
$software-factory --rerun=stage4.architecture
```

## 3. 一个端到端示例

```text
You → $software-factory 帮我做一个内部用的"OKR 周报系统"
Codex:
  Phase 0  扫描 skill-manifest → 缺 coding / product-design → 询问 → 安装
  Phase 1  Idea Mode → 补全角色 / 范围 / 数据字典
  Phase 1  写入 workspace/requirements/PRD.md + 三件套
  Phase 2  Stage 2 渲染原型
          Stage 4 写架构 + API + DB
          Stage 5 生成 Spring Boot 工程
          Stage 6 mvn package + java -jar
          Stage 7 浏览器打开首页 + 截图
          Stage 8 测试 / 评审
Delivery 给你 final-report.md + screenshots/*.png
```

## 4. 调试小技巧

- 想看当前状态：`$software-factory status`
- 想强停：删 `workspace/.workflow-state.json` 然后下次触发 `--resume`
- 想单独跑 Stage：`$software-factory --rerun=<stageId>`

## 5. 故障处理

| 现象 | 多数情况下怎么办 |
|------|------------------|
| Phase 0 装 Skill 卡住 | 看 `phase0/install-log.md`；多数是 marketplace 凭据问题 |
| Stage 4 一直出差异 | PRD 与 architecture 互相覆盖；固定从 PRD 生成 architecture |
| Stage 6 启动失败 | 看 `runtime.log`；先做 `mvn -DskipTests package` 验证 |
| Stage 7 截图空白 | 等应用真正起来再发请求；用 `actuator/health` 探活 |