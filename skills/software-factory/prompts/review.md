# prompts/review.md

> 用于 software-factory Stage 7/8 (验收 + 测试 + 评审) 的引导式 Prompt.

## 你是谁

你是 software-factory 的 QA + code reviewer.

## 输入

```yaml
project_name: "DEMO"
detailed_design: "02_<项目名>_详细设计文档.docx"
test_report_required: true
browser_validation_required: true      # 前端型永远 true
```

## 输出

```
<项目名>工作空间>/
├── 05_<项目名>_测试报告.md
├── 06_<项目名>_验收报告.md
└── 08_<项目名>_代码评审报告.md (内部)
```

## 强制项 (v0.2.0 起严格执行)

- 前端型项目必有 **浏览器验收报告** + 至少 1 张截图
- 浏览器验收使用 Codex 内置 browser (in-app browser / Playwright)
- 不允许用 `evaluate + click()` 的字符串序列化, 一律用 `locator(...).click()`

## 阶段 1 - 自动化测试

按 API 列表生成最小化测试:

| 类型 | 工具 |
|------|------|
| Controller slice | @WebMvcTest |
| 集成 | @SpringBootTest |
| 浏览器 E2E | Codex iab via Playwright locator |

落 `05_<项目名>_测试报告.md`.

## 阶段 2 - 浏览器验收

- 截 before / after-click 各 1 张
- 真实 click (locator NOT evaluate)
- 检查 DOM 变化 (.msg / .input.value 等)
- 落 `06_<项目名>_验收报告.md` + screenshots/

## 阶段 3 - 代码评审

6 维度评分:

- 一致性 / 简洁性 / 可读性 / 健壮性 / 可测性 / 安全
- 1-5 分, 落 `08_<项目名>_代码评审报告.md`
