# prompts/review.md

> 用于 software-factory Stage 7/8 (验收 + 测试 + 评审) 的引导式 Prompt.
> v0.6.2: Codex Desktop 的 Stage 8 强制打开右侧 in-app browser；Codex CLI 没有该面板时，走内置 Playwright WebM 录屏兜底，并强制显示模拟鼠标位置与点击波纹.

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

## 阶段 2 - 浏览器验收 (v0.5.4 — 按实测 iab API 重写)

**为什么升级到强约束**: 每次跑 DEMO 都要"实时看到测试过程". Codex 对话框右边的 in-app browser 面板就是窗口. v0.5.2 起强制开面板, v0.5.4 起又踩实了 iab 的 API 现实, 把"听着能用其实 hang/未实现"的 API 全部排除.

### ⚠️ iab API 现实 (v0.5.4 踩出来的, 必读)

| API | 状态 | 现象 |
|-----|------|------|
| `tab.screenshot({path})`            | ❌ hang | CDP Page.captureScreenshot 长时超时 (Statsig analytics 阻塞) |
| `tab.content.export()`             | ❌ 抛错 | `Codex in-app browser does not support command "tab_content_export"` |
| `tab.playwright.evaluate(...)`     | ❌ 返回 undefined | 不论返回 primitive / object, 都丢失 |
| `tab.playwright.domSnapshot()`     | ❌ 抛错 | `incrementalAriaSnapshot is not a function` |
| `tab.dom_cua.get_visible_dom()`    | ✅ 可用 | 返回 node_id 字符串, 用来 locator |
| `tab.dom_cua.click({node_id})`     | ✅ 可用 | DOM 节点驱动的 click |
| `tab.dom_cua.type({text})`         | ✅ 可用 | 在当前焦点元素 type |
| `tab.cua.click(x,y)`               | ✅ 可用 | 坐标 / 焦点驱动 |
| `tab.cua.type({text})`             | ✅ 可用 | 焦点驱动 type |

### 步骤 0 - 初始化 in-app browser (强制)

```javascript
// 在 mcp__node_repl__js 里跑:
if (globalThis.agent?.browsers == null) {
  const { setupBrowserRuntime } = await import(
    "C:/Users/test/.codex/plugins/cache/openai-bundled/browser/26.623.141536/scripts/browser-client.mjs"
  );
  await setupBrowserRuntime({ globals: globalThis });
}
const browser = await agent.browsers.get("iab");
const vis = await browser.capabilities.get("visibility");
await vis.set(true);                   // ❗ 强制: 让用户在 Codex 右侧看到
nodeRepl.write(await browser.documentation());
```

### 步骤 1 - 找 tab + 让用户看到页面

```javascript
const tabs = await browser.tabs.list();
const tab = await browser.tabs.get(tabs[0].id);   // 取已开 tab (避免重复)
// 若 URL 不对, 用 goto
if (!(await tab.url()).match(/localhost:\\d+/)) {
  await tab.goto("http://localhost:8082/");
}
```

### 步骤 2 - 用 dom_cua 取节点 ID + 交互 (核心)

```javascript
// 1. 拿当前 DOM 节点 ID 列表
const dom = await tab.dom_cua.get_visible_dom();
// dom 形如: '<input node_id=1 placeholder="..." />\\n<button node_id=2>打个招呼</button>'

// 2. 用 node_id click + type (强制按 node_id, 不允许靠 selector)
await tab.dom_cua.click({ node_id: "1" });        // focus 到 input
await tab.dom_cua.type({ text: "hello world" });  // 输入
await tab.dom_cua.click({ node_id: "2" });        // 点按钮

// 3. 再读 DOM 验证 (避免中间态)
const dom2 = await tab.dom_cua.get_visible_dom();
```

> 每次交互后, 通过 `get_visible_dom()` 重新读 DOM 验证状态变化.

### 步骤 3 - 截图 (若用户要求存档 PNG)

**优先**: 让用户在 Codex 右侧面板肉眼验证, 不用落盘截图.
**Desktop 兜底**: 若必须落盘 PNG, 起本地 headless chrome:
```
"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --disable-gpu --no-sandbox --hide-scrollbars --window-size=1280,720 --virtual-time-budget=5000 --screenshot=<workspace>/screenshots/08-01-home.png <url>
```

### 步骤 3.5 - Codex CLI 无侧边栏时的合规替代

Codex CLI 没有 Desktop 的右侧 in-app browser，不能执行 `visibility.set(true)`，也不能在报告里声称用户看到了侧边栏。此时执行 Skill 内置脚本：

```bash
py -3 -m pip install playwright
py -3 -m playwright install chromium
python "$CODEX_HOME/skills/software-factory/scripts/stage8_run_acceptance.py" \
  --url http://localhost:<port>/ \
  --out <workspace>/08b_acceptance_artifacts \
  --scenario <workspace>/08b_stage8_scenario.json \
  --cursor-delay-ms 220
```

脚本使用 Playwright locator 驱动 CLI 浏览器，逐步落 PNG，录制 WebM，并生成 `acceptance.json`（含 `runtime`、步骤、页面错误、控制台错误、`cursor_overlay`）。录屏中必须看到高对比度箭头跟随 locator 移动，点击时出现黄色波纹；不得关闭光标后交付。这是 CLI 的证据采集分支，不是 Desktop 侧边栏的替代显示；验收报告必须写明运行时和原因。

### 步骤 4 - 写验收报告

落 `06_<项目名>_验收报告.md`, **必须**含以下关键词:
- `"in-app browser"` (Desktop 分支至少 1 次；CLI 分支要说明未使用原因)
- `"右侧面板"` 或 `"iab 面板"` (Desktop 分支至少 1 次)
- `"dom_cua"` 或 `"node_id"` (Desktop 分支至少 1 次)
- CLI 分支额外列 `runtime: cli-playwright`、WebM 路径和 `acceptance.json`
- 列出每步操作和 PASS/FAIL 结果
- 列 URL + 端口 + ISO 时间戳

### ❌ v0.5.4 起明确禁止

- ❌ `tab.screenshot({path})` — 已知会 hang, 不许重试
- ❌ `tab.content.export()` — 已知 iab 不支持
- ❌ `tab.playwright.evaluate(...)` — 已知返回 undefined, 不要指望
- ❌ `tab.playwright.domSnapshot()` — 已知 `incrementalAriaSnapshot is not a function`
- ❌ 在 Codex Desktop 用 `chromium.launch({headless:true})` 绕过右侧面板 (CLI 分支除外)
- ❌ 用 selector (`button.send-btn`) 选节点 — iab 的 dom_cua 没有 selector 入口, 必须 node_id


## 阶段 1 - 自动化测试

按 API 列表生成最小化测试:

| 类型 | 工具 |
|------|------|
| Controller slice | @WebMvcTest |
| 集成 | @SpringBootTest |
| 浏览器 E2E | Desktop 用 Codex in-app browser + dom_cua；CLI 用 Skill 内置 Playwright runner |

落 `05_<项目名>_测试报告.md`.

## 阶段 3 - 代码评审

6 维度评分:

- 一致性 / 简洁性 / 可读性 / 健壮性 / 可测性 / 安全
- 1-5 分, 落 `08_<项目名>_代码评审报告.md`
