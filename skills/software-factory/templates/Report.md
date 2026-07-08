# Delivery Report — {{project_name}}

> 由 `software-factory` 在 Phase 2 全部 Stage 完成时产出。
> 这是给**用户**看的总结，不是开发文档。

## 1. 一句话总结

<!-- 这次跑完 software-factory 之后，用户拿到了什么 -->

## 2. 交付物清单

- [ ] `workspace/requirements/PRD.md`
- [ ] `workspace/design/architecture.md`
- [ ] `workspace/development/source-code/`（可运行代码）
- [ ] `workspace/testing/test-report.md`
- [ ] `workspace/testing/validation-report.md`
- [ ] `workspace/delivery/screenshots/`

## 3. 运行方式

```bash
cd workspace/development/source-code
mvn -DskipTests package
java -jar target/*.jar
# 默认 http://localhost:8080
```

## 4. 验证结果

| Stage | 状态 | 备注 |
|-------|------|------|
| Phase 0 环境准备 | ✅ / ⚠️ / ❌ | |
| Phase 1 需求评估 | ✅ / ⚠️ / ❌ | |
| Stage 1 需求规格 | ✅ / ⚠️ / ❌ | |
| Stage 4 架构设计 | ✅ / ⚠️ / ❌ | |
| Stage 5 实现 | ✅ / ⚠️ / ❌ | |
| Stage 6 构建运行 | ✅ / ⚠️ / ❌ | |
| Stage 7 浏览器验证 | ✅ / ⚠️ / ❌ | |
| Stage 8 测试 / 评审 | ✅ / ⚠️ / ❌ | |

## 5. 浏览器截图

> 截图存放在 `delivery/screenshots/`，按页面 / 流程命名。

## 6. 已知问题 / 后续

| 项 | 影响 | 建议 |
|----|------|------|
| | | |

## 7. 复跑指引

```text
$software-factory --resume          # 从中断处继续
$software-factory --rerun=stage5    # 单 Stage 重跑
$software-factory --dry-run         # 仅 Phase 0/1
```
