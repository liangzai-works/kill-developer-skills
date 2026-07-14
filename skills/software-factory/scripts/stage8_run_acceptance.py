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

from playwright.sync_api import Page, sync_playwright


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


def run_action(page: Page, action: dict[str, Any], timeout_ms: int) -> None:
    if "click" in action:
        page.locator(action["click"]).click(timeout=timeout_ms)
    elif "fill" in action:
        payload = action["fill"]
        page.locator(payload["selector"]).fill(str(payload.get("text", "")), timeout=timeout_ms)
    elif "check" in action:
        page.locator(action["check"]).check(timeout=timeout_ms)
    elif "uncheck" in action:
        page.locator(action["uncheck"]).uncheck(timeout=timeout_ms)
    elif "press" in action:
        payload = action["press"]
        page.locator(payload["selector"]).press(str(payload["key"]), timeout=timeout_ms)
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
        initial_state = read_state(page, selectors)

        for index, step in enumerate(scenario.get("steps", [])):
            key = str(step.get("key", f"{index:02d}_step"))
            entry: dict[str, Any] = {"key": key, "label": step.get("label", key)}
            started = time.time()
            try:
                for action in step.get("actions", []):
                    run_action(page, action, args.timeout_ms)
                wait_ms = int(step.get("wait_ms", 500))
                page.wait_for_timeout(wait_ms)
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
