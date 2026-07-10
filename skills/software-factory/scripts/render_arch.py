#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_arch.py - 架构图自动生成 (software-factory 内置能力)

输入:
  - arch.md / arch.yaml / arch.json  分层架构描述 (顶层 -> 底层)
  - 也接受 --layers CLI 参数直接传 JSON

输出:
  - PNG 文件

依赖:
  - matplotlib (pip install matplotlib)

用法:
  python render_arch.py --src 03_架构设计.md --out 03_架构图.png
  python render_arch.py --layers '[["业务模块A","首页"],["业务模块B","节点管理"]]'
  python render_arch.py --check

退出码: 0=成功, 1=输入错误, 2=渲染失败

设计约束 (v0.5.1):
  - 业务模块强制: 默认示例改为业务模块维度, 严禁 SpringBoot 技术分层示例
  - agent 应从需求规格里抽取业务模块列表后传入
"""
import argparse
import json
import re
import sys
from pathlib import Path

FONT_CANDIDATES = [
    "SimHei", "Microsoft YaHei", "PingFang SC", "Microsoft JhengHei",
    "Heiti SC", "STHeiti", "Source Han Sans CN", "Noto Sans CJK SC",
    "WenQuanYi Micro Hei", "Arial Unicode MS", "DejaVu Sans",
]

LAYER_COLORS = [
    "#E3F2FD", "#BBDEFB", "#90CAF9", "#64B5F6",
    "#42A5F5", "#1E88E5", "#1565C0",
]
TEXT_COLOR = "#1A237E"
EDGE_COLOR = "#1976D2"
TITLE_COLOR = "#0D47A1"

# v0.5.1: 默认示例改为业务模块维度. 严禁 SpringBoot 技术分层作为示例.
# 见 prompts/architecture.md 业务模块强约束.
DEFAULT_EXAMPLE_LAYERS = [
    ["业务模块A", "示例: 首页 / 概览仪表盘 / 关键指标"],
    ["业务模块B", "示例: 节点管理 / 核心 CRUD + 状态机"],
    ["业务模块C", "示例: 用户管理 / 登录鉴权 + 角色"],
    ["数据访问", "基础设施: Repository / DB 落地 (非业务模块, 仅占位)"],
]


def pick_font() -> str:
    try:
        import matplotlib.font_manager as fm
        available = {f.name for f in fm.fontManager.ttflist}
    except Exception:
        return "DejaVu Sans"
    for name in FONT_CANDIDATES:
        if name in available:
            return name
    return "DejaVu Sans"


def check_deps() -> int:
    try:
        import matplotlib  # noqa: F401
    except Exception:
        print("[FAIL] matplotlib 不可用, 安装: pip install matplotlib")
        return 2
    print(f"[OK] matplotlib ok, CN font: {pick_font()}")
    return 0


def parse_layers_from_md(md_path: Path) -> list:
    text = md_path.read_text(encoding="utf-8")
    layers = []
    table_rows = re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", text, re.MULTILINE)
    if table_rows:
        for row in table_rows:
            name, comp = row
            # 跳过表头 (层 / 层级 / layer / level 等关键词) 与分隔行
            if name.lower() in ("层", "层级", "layer", "level"):
                continue
            if name.startswith("---") or comp.startswith("---"):
                continue
            # 跳过 markdown 表头说明中的 "业务模块" / "主要组件"
            if name.strip() in ("业务模块", "模块", "模块名", "名称"):
                continue
            if comp.strip() in ("主要组件", "组件", "职责", "问题描述"):
                continue
            layers.append([name.strip(), comp.strip()])
        if layers:
            return layers

    current_layer = None
    current_comps = []
    for line in text.splitlines():
        m_head = re.match(r"^#{1,6}\s+(.+)$", line)
        if m_head:
            if current_layer:
                layers.append([current_layer, ", ".join(current_comps) if current_comps else "-"])
            current_layer = m_head.group(1).strip()
            current_layer = re.sub(r"^\d+[\.\u3001\)\.]\s*", "", current_layer)
            current_comps = []
        else:
            m_li = re.match(r"^\s*[-*]\s+(.+)$", line)
            if m_li and current_layer:
                comp = m_li.group(1).strip()
                comp = re.sub(r"\*\*(.+?)\*\*", r"\1", comp)
                comp = re.sub(r"`(.+?)`", r"\1", comp)
                current_comps.append(comp)
    if current_layer:
        layers.append([current_layer, ", ".join(current_comps) if current_comps else "-"])
    return layers


def parse_layers_from_json(j: list) -> list:
    out = []
    for item in j:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append([str(item[0]), str(item[1])])
        elif isinstance(item, dict):
            out.append([str(item.get("layer", item.get("name", "?"))),
                        str(item.get("components", item.get("comp", "-")))])
    return out


def render(layers: list, out_path: Path, title: str = "系统架构图") -> int:
    if not layers:
        print("[FAIL] layers 为空")
        return 1
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except Exception as e:
        print(f"[FAIL] matplotlib 不可用: {e}")
        return 2

    font_name = pick_font()
    matplotlib.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    n = len(layers)
    fig_height = max(4, 0.85 * n + 1.5)
    fig, ax = plt.subplots(figsize=(11, fig_height), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, n + 1); ax.axis("off")

    ax.text(5, n + 0.55, title, ha="center", va="center",
            fontsize=16, fontweight="bold", color=TITLE_COLOR)

    box_w, box_h, cx = 9.0, 0.7, 5.0
    for i, (name, comp) in enumerate(layers):
        y = n - i - 0.5
        color = LAYER_COLORS[i % len(LAYER_COLORS)]
        box = FancyBboxPatch((cx - box_w/2, y - box_h/2), box_w, box_h,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=1.5, edgecolor=EDGE_COLOR, facecolor=color)
        ax.add_patch(box)
        ax.text(cx - box_w/2 + 0.25, y, name, ha="left", va="center",
                fontsize=12, fontweight="bold", color=TEXT_COLOR)
        comp_text = comp if len(comp) < 60 else comp[:57] + "..."
        ax.text(cx + box_w/2 - 0.25, y, comp_text, ha="right", va="center",
                fontsize=9, color=TEXT_COLOR)
        if i < n - 1:
            ax.annotate("", xy=(cx, (n - (i+1) - 0.5) + box_h/2),
                        xytext=(cx, y - box_h/2),
                        arrowprops=dict(arrowstyle="->", color=EDGE_COLOR,
                                        lw=1.2, shrinkA=2, shrinkB=2))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[OK] 架构图已生成: {out_path}  size={out_path.stat().st_size}B  font={font_name}  layers={n}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="架构图自动生成 (software-factory 内置能力)")
    ap.add_argument("--src", help="架构描述文件 (.md / .yaml / .json)")
    ap.add_argument("--layers", help="JSON: '[[\"业务模块A\",\"...\"],...]'")
    ap.add_argument("--out", default="03_架构图.png")
    ap.add_argument("--title", default="系统架构图")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        sys.exit(check_deps())

    layers = []
    if args.src:
        src = Path(args.src)
        if not src.exists():
            print(f"[FAIL] 文件不存在: {src}"); sys.exit(1)
        suf = src.suffix.lower()
        if suf == ".json":
            data = json.loads(src.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data = data.get("layers", data.get("architecture", []))
            layers = parse_layers_from_json(data)
        elif suf in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(src.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data = data.get("layers", data.get("architecture", []))
                layers = parse_layers_from_json(data)
            except ImportError:
                layers = parse_layers_from_md(src)
        else:
            layers = parse_layers_from_md(src)
    elif args.layers:
        try:
            data = json.loads(args.layers)
            layers = parse_layers_from_json(data)
        except json.JSONDecodeError as e:
            print(f"[FAIL] JSON 解析失败: {e}"); sys.exit(1)
    else:
        # v0.5.1: 默认示例改为业务模块维度 (而非技术分层)
        layers = DEFAULT_EXAMPLE_LAYERS
        print(f"[INFO] 未指定输入, 用默认 {len(layers)} 个业务模块示例")
        print("[INFO] ⚠️  这是占位示例, 请从需求规格里抽取真实业务模块后用 --src 或 --layers 重画")

    if not layers:
        print("[FAIL] 未解析到任何层"); sys.exit(1)
    sys.exit(render(layers, Path(args.out), title=args.title))


if __name__ == "__main__":
    main()