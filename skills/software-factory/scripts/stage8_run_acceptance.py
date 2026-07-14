#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 8 CLI 兜底：Playwright 交互、截图、WebM 和 JSON 报告。"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page, sync_playwright


CURSOR_ID = "__stage8_visible_cursor"
CURSOR_SCRIPT = f"""
() => {{
  if (document.getElementById('{CURSOR_ID}')) return;
  const style = document.createElement('style');
  style.textContent = `
    #{CURSOR_ID} {{
      position: fixed;
      left: 0;
      top: 0;
      width: 28px;
      height: 34px;
      z-index: 2147483647;
      pointer-events: none;
      opacity: 0;
      transform: translate3d(24px, 24px, 0);
      transition: transform 220ms cubic-bezier(.2,.8,.2,1), opacity 120ms ease;
      filter: drop-shadow(0 2px 3px rgba(0,0,0,.65));
    }}
    #{CURSOR_ID}.stage8-visible {{ opacity: 1; }}
    #{CURSOR_ID} svg {{ display: block; width: 23px; height: 29px; }}
    #{CURSOR_ID} .stage8-ripple {{
      position: absolute;
      left: -7px;
      top: -7px;
      width: 30px;
      height: 30px;
      border: 3px solid #ffdd57;
      border-radius: 999px;
      opacity: 0;
      transform: scale(.35);
    }}
    #{CURSOR_ID}.stage8-click .stage8-ripple {{
      animation: stage8-cursor-ripple 520ms ease-out;
    }}
    @keyframes stage8-cursor-ripple {{
      0% {{ opacity: 1; transform: scale(.35); }}
      100% {{ opacity: 0; transform: scale(1.55); }}
    }}
  `;
  document.documentElement.appendChild(style);
  const cursor = document.createElement('div');
  cursor.id = '{CURSOR_ID}';
  cursor.setAttribute('aria-hidden', 'true');
  cursor.innerHTML = `
    <svg viewBox="0 0 24 30" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 1.5V25.5L8.7 19.2L13.2 28.2L17.4 26.1L13 17.3H22L2 1.5Z"
            fill="#151515" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>
    </svg>
    <span class="stage8-ripple"></span>`;
  document.documentElement.appendChild(cursor);
}}
"""


def load_scenario(path: str | None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {"steps": [{"key": "00_initial_load", "label": "加载页面", "wait_ms": 1000}]}


def page_text(page: Page, selector: str) -> str:
    return (page.text_content(selector) or "").strip()


def read_state(page: Page, selectors: dict[str, str]) -> dict[str, str]:
    state: dict[str, str] = {}
    for key, selector in selectors.items():
        try:
            state[key] = page_text(page, selector)
        except Exception:
            state[key] = ""
    return state


def ensure_cursor(page: Page) -> None:
    page.evaluate(CURSOR_SCRIPT)


def set_cursor_position(page: Page, x: float, y: float, delay_ms: int) -> None:
    ensure_cursor(page)
    page.evaluate(
        f"""
        (position) => {{
          const cursor = document.getElementById('{CURSOR_ID}');
          cursor.style.transform = `translate3d(${{position.x}}px, ${{position.y}}px, 0)`;
          cursor.classList.add('stage8-visible');
        }}
        """,
        {"x": round(x, 1), "y": round(y, 1)},
    )
    page.mouse.move(x, y, steps=10)
    page.wait_for_timeout(delay_ms)


def move_cursor_to(page: Page, locator: Locator, timeout_ms: int, delay_ms: int) -> None:
    locator.scroll_into_view_if_needed(timeout=timeout_ms)
    box = locator.bounding_box(timeout=timeout_ms)
    if box is None:
        raise AssertionError("目标控件没有可见区域，无法显示录屏光标")
    set_cursor_position(
        page,
        box["x"] + box["width"] / 2,
        box["y"] + box["height"] / 2,
        delay_ms,
    )


def pulse_cursor(page: Page) -> None:
    page.evaluate(
        f"""
        () => {{
          const cursor = document.getElementById('{CURSOR_ID}');
          cursor.classList.remove('stage8-click');
          void cursor.offsetWidth;
          cursor.classList.add('stage8-click');
        }}
        """
    )


def run_action(page: Page, action: dict[str, Any], timeout_ms: int, cursor_delay_ms: int) -> None:
    if "click" in action:
        locator = page.locator(action["click"])
        move_cursor_to(page, locator, timeout_ms, cursor_delay_ms)
        locator.click(timeout=timeout_ms)
        pulse_cursor(page)
    elif "fill" in action:
        payload = action["fill"]
        locator = page.locator(payload["selector"])
        move_cursor_to(page, locator, timeout_ms, cursor_delay_ms)
        pulse_cursor(page)
        locator.fill(str(payload.get("text", "")), timeout=timeout_ms)
    elif "check" in action:
        locator = page.locator(action["check"])
        move_cursor_to(page, locator, timeout_ms, cursor_delay_ms)
        locator.check(timeout=timeout_ms)
        pulse_cursor(page)
    elif "uncheck" in action:
        locator = page.locator(action["uncheck"])
        move_cursor_to(page, locator, timeout_ms, cursor_delay_ms)
        locator.uncheck(timeout=timeout_ms)
        pulse_cursor(page)
    elif "press" in action:
        payload = action["press"]
        locator = page.locator(payload["selector"])
        move_cursor_to(page, locator, timeout_ms, cursor_delay_ms)
        pulse_cursor(page)
        locator.press(str(payload["key"]), timeout=timeout_ms)
    elif "wait_for" in action:
        payload = action["wait_for"]
        page.locator(payload["selector"]).wait_for(
            state=payload.get("state", "visible"),
            timeout=payload.get("timeout_ms", timeout_ms),
        )
    elif "wait_ms" in action:
        page.wait_for_timeout(int(action["wait_ms"]))
    elif "assert_text" in action:
        payload = action["assert_text"]
        actual = page_text(page, payload["selector"])
        expected = str(payload["contains"])
        if expected not in actual:
            raise AssertionError(f"{payload['selector']} 不包含 {expected!r}，实际为 {actual!r}")
    else:
        raise ValueError(f"不支持的 action: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 8 CLI Playwright 验收与录屏")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--scenario", help="场景 JSON；省略时执行加载页冒烟")
    parser.add_argument("--video-name", default="stage8_acceptance.webm")
    parser.add_argument("--viewport-w", type=int, default=1280)
    parser.add_argument("--viewport-h", type=int, default=720)
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--cursor-delay-ms", type=int, default=220)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out)
    frames_dir = out_dir / "frames"
    video_dir = out_dir / "video"
    frames_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)
    scenario = load_scenario(args.scenario)
    selectors = scenario.get("state_selectors", {})
    timeline: list[dict[str, Any]] = []
    errors: list[str] = []
    console_logs: list[dict[str, str]] = []
    console_errors: list[dict[str, str]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            viewport={"width": args.viewport_w, "height": args.viewport_h},
            locale="zh-CN",
            record_video_dir=str(video_dir),
            record_video_size={"width": args.viewport_w, "height": args.viewport_h},
        )
        page = context.new_page()

        def on_console(message: Any) -> None:
            item = {"type": message.type, "text": message.text}
            console_logs.append(item)
            if message.type == "error":
                console_errors.append(item)

        page.on("console", on_console)
        page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
        page.goto(args.url, wait_until="networkidle", timeout=args.timeout_ms)
        ensure_cursor(page)
        set_cursor_position(page, args.viewport_w / 2, args.viewport_h / 2, args.cursor_delay_ms)
        initial_state = read_state(page, selectors)

        for index, step in enumerate(scenario.get("steps", [])):
            key = str(step.get("key", f"{index:02d}_step"))
            entry: dict[str, Any] = {"key": key, "label": step.get("label", key)}
            started = time.time()
            try:
                for action in step.get("actions", []):
                    run_action(page, action, args.timeout_ms, args.cursor_delay_ms)
                wait_ms = int(step.get("wait_ms", 500))
                page.wait_for_timeout(wait_ms)
                ensure_cursor(page)
                shot = f"frame_{key}.png"
                page.screenshot(path=str(frames_dir / shot), full_page=False)
                entry.update({
                    "wait_ms": wait_ms,
                    "shot": shot,
                    "state": read_state(page, selectors),
                    "elapsed_ms": round((time.time() - started) * 1000, 1),
                })
            except Exception as error:
                errors.append(f"step {key} failed: {error}")
                entry["error"] = str(error)
            timeline.append(entry)

        final_state = read_state(page, selectors)
        context.close()
        browser.close()

    video_files = sorted(video_dir.glob("*.webm"))
    video_target = out_dir / args.video_name
    if video_files:
        shutil.move(str(video_files[0]), str(video_target))

    report = {
        "tool": "stage8_run_acceptance.py",
        "runtime": "cli-playwright",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "url": args.url,
        "video": video_target.name if video_target.exists() else None,
        "frames": str(frames_dir),
        "timeline": timeline,
        "snapshot_initial": initial_state,
        "snapshot_final": final_state,
        "errors": errors,
        "console_log_count": len(console_logs),
        "console_error_count": len(console_errors),
        "cursor_overlay": True,
        "cursor_delay_ms": args.cursor_delay_ms,
    }
    (out_dir / "acceptance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "video": report["video"],
        "frames": report["frames"],
        "errors": errors,
        "console_error_count": len(console_errors),
    }, ensure_ascii=True))
    return 0 if not errors and not console_errors else 2


if __name__ == "__main__":
    sys.exit(main())
