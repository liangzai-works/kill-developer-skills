# prompts/review.md

> 用于 software-factory Stage 7/8 (验收 + 测试 + 评审) 的引导式 Prompt.
> v0.5.2: Stage 8 强制打开 Codex 右侧 in-app browser 面板, 不允许纯 headless 跑.

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

## ⚠️ 阶段 2 - 浏览器验收 (v0.5.2 起强制打开右侧 in-app browser 面板)

**为什么升级到强约束**: 用户每次跑 DEMO 都要"实时看到测试过程", 而 in-app browser 面板就是 Codex 对话框右边那个浏览器面板, agent 用 `$browser control-in-app-browser` skill 调一下就开了, 跟着用户能在屏幕右边实时看到测试; 之前是 agent 自覚开, 现在是 skill **强制要求**开.

### 步骤 0 - 初始化 in-app browser (强制)

```javascript
// 在 mcp__node_repl__js 里跑:
if (globalThis.agent?.browsers == null) {
  const { setupBrowserRuntime } = await import(
    "C:/Users/test/.codex/plugins/cache/openai-bundled/browser/26.623.141536/scripts/browser-client.mjs"
  );
  await setupBrowserRuntime({ globals: globalThis });
}
globalThis.browser = await agent.browsers.get("iab");
nodeRepl.write(await browser.documentation());
```

> 完整调用规约见 `control-in-app-browser` skill 的 SKILL.md. 不要跳过这一步直接用 `chromium.launch({ headless: true })`.

### 步骤 1 - 打开右侧面板 + 导航

```javascript
const tab = await browser.contexts()[0].newPage();
await tab.goto("http://localhost:8080/");           // service 地址, <项目>健康地址
await tab.screenshot({ path: "<workspace>/screenshots/08-01-home-opened.png" });
```

> 用户应能在 Codex 对话框**右侧**看到这个浏览器面板. 如果没看到, 自己 Win+→ 把 Codex 拖到屏幕左半边, 浏览器面板自动会浮现在右半边.

### 步骤 2 - 真实交互 (locator, 不是 evaluate)

```javascript
await tab.locator("button.send-btn").click();      // 等于真实点击, 右侧面板同步显示
await tab.locator("input.msg").fill("hello");
await tab.locator("button.submit").click();
await tab.waitForSelector(".response-row", { timeout: 5000 });
await tab.screenshot({ path: "<workspace>/screenshots/08-02-after-click.png" });
```

每一步交互后, **必须**截图存 `screenshots/<NN>-<语义>.png`, 写到 `06_<项目名>_验收报告.md` 里.

### 步骤 3 - 写验收报告

落 `06_<项目名>_验收报告.md`, 必须含:

| Section | 内容 |
|---------|------|
| 测试时间 | ISO 时间戳 |
| 测试方式 | Codex in-app browser (右侧面板可见) |
| 测试地址 | URL + 端口 |
| 场景清单 | 按 `04b_<项目名>_UI设计.md` 走, 每场景 PASS/FAIL |
| 截图引用 | `screenshots/08-*.png` 列表 |
| 已知问题 | 任何步骤 fail / 异常 / 建议 |

### ❌ 不允许做的

- ❌ 用 `chromium.launch({ headless: true })` 纯 headless 跑完后只交 screenshots
- ❌ 不打开右侧 in-app browser 面板, 用户没法实时看到测试过程
- ❌ 用 `page.evaluate("document.querySelector('button').click()")` 字符串序列化点击 (改成 locator)
- ❌ 跳过交互步骤只跑 API 调用 (验收报告失去意义)
- ❌ 截图前不 `waitForSelector`, 截到中间态

### (可选) ffmpeg 桌面录屏

如果用户说"想要录屏 mp4 看后期回放", 验收集群在前后台启 ffmpeg:

```bash
# 后台启 (后台, stderr 丢弃)
ffmpeg -f gdigrab -framerate 15 -i desktop -t 60 "<workspace>/screenshots/08-recording.mp4" -y 2>/dev/null &
$REC_PID=$!
# ... 跑测试 ...
kill $REC_PID 2>/dev/null
```

落 `screenshots/08-recording.mp4`. 默认不开 (录屏很占 CPU), 用户明确说"录下来"才走.

## 阶段 1 - 自动化测试

按 API 列表生成最小化测试:

| 类型 | 工具 |
|------|------|
| Controller slice | @WebMvcTest |
| 集成 | @SpringBootTest |
| 浏览器 E2E | Codex in-app browser via Playwright locator (步骤见阶段 2) |

落 `05_<项目名>_测试报告.md`.

## 阶段 3 - 代码评审

6 维度评分:

- 一致性 / 简洁性 / 可读性 / 健壮性 / 可测性 / 安全
- 1-5 分, 落 `08_<项目名>_代码评审报告.md`