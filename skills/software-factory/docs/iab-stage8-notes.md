# Codex in-app browser (iab) Stage 8 实战踩坑 (v0.5.4)

> 这是从真实测试里摸出来的"看似能用其实坏"的 API 黑名单, 写进 skill 是为了省 token.
>
> 适用: Codex 桌面版 (iab) 不适用 Chrome 外部 skill.

## 推荐 API (实测可用)

| API | 说明 |
|-----|------|
| `tab.dom_cua.get_visible_dom()`            | 返回带 `node_id` 的 DOM 字符串, 用于后续 click/type |
| `tab.dom_cua.click({node_id: "<id>"})`     | DOM 节点驱动的 click |
| `tab.dom_cua.type({text: "..."})`          | 在当前焦点元素 type |
| `tab.cua.click(x, y)`                       | 坐标驱动的 click (兜底) |
| `tab.cua.type({text: "..."})`              | 焦点驱动 type (兜底) |
| `(await browser.capabilities.get("visibility")).set(true)` | 让用户在右侧看到浏览器 |

## 黑名单 (实测会 hang / undefined / 抛错)

| API | 现象 |
|-----|------|
| `tab.screenshot({path})`               | **hang** at `Page.captureScreenshot` (Statsig analytics 阻塞, 30s+ 还没返回) |
| `tab.content.export()`                | 抛 `Codex in-app browser does not support command "tab_content_export"` |
| `tab.playwright.evaluate("() => ...")` | 永远返回 `undefined`, 不论返回 primitive / object |
| `tab.playwright.domSnapshot()`        | 抛 `TypeError: o.incrementalAriaSnapshot is not a function` |
| `tab.playwright.locator("button")`    | 类型错误 / 不会按 selector 解析 |
| `tab.page` 假设                       | `page` 字段在 iab tab 上不存在 |

## 完整最小可运行样板 (DEMO 项目验证过)

```javascript
// 1. 初始化 (kernel 重启后必跑)
if (globalThis.agent?.browsers == null) {
  const m = await import(
    "C:/Users/test/.codex/plugins/cache/openai-bundled/browser/26.623.141536/scripts/browser-client.mjs"
  );
  await m.setupBrowserRuntime({ globals: globalThis });
}

// 2. 取 iab + 强制显示右侧面板
const browser = await agent.browsers.get("iab");
const vis = await browser.capabilities.get("visibility");
await vis.set(true);

// 3. 拿 tab, 没有就新建 (这里 demo 假设用户已经手动打开过)
const tabs = await browser.tabs.list();
const tab = await browser.tabs.get(tabs[0].id);

// 4. 拿到 DOM 节点 ID
const dom = await tab.dom_cua.get_visible_dom();
// dom 形如:
// <input node_id=1 placeholder="例如 Codex" />
// <button node_id=2>打个招呼</button>

// 5. 交互
await tab.dom_cua.click({ node_id: "1" });   // focus input
await tab.dom_cua.type({ text: "v0.5.4 验收" });
await tab.dom_cua.click({ node_id: "2" });   // click button

// 6. 再读 DOM 验证状态
const dom2 = await tab.dom_cua.get_visible_dom();
// 多一行: <generic node_id=N>👋  你好, v0.5.4 验收 ...</generic>

// 7. 截图兜底: 用本地 headless chrome 写 PNG 到工作空间
// (iab 自己的截图 API hang, 必须外部兜底)
```

## Stage 8 验收报告 必含关键词

- "in-app browser" (≥1)
- "iab 面板" 或 "右侧面板" (≥1)
- "dom_cua" 或 "node_id" (≥1)
- 列出 `dom_cua.click({node_id:"N"})` 风格的操作日志
- URL + 端口 + ISO 时间戳

## 历史

- v0.5.2: 引入 "Stage 8 强制打开右侧 iab 面板" 约束
- v0.5.3: 改 Heading 编号, 与 iab 无关
- **v0.5.4 (本次)**: iab API 现实落库 — 把"看起来行但 hang/未实现"的 API 全部禁掉
