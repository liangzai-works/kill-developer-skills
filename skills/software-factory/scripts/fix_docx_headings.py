#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_docx_headings.py - 修复详细设计 .docx 标题双重编号 bug

问题:
  公司详细设计模板的 styles.xml 把 Heading 1/2/3 绑到 numbering.xml 的某个 numId
  (本仓库随附的模板就是 numId=5).
  Word 打开后会"自动"给段落加 "1." "1.1" "1.1.1" 前缀.
  我们手动写了中文"一、" / 阿拉伯"1.1"编号, 渲染时变成 "1  一. 概述" 这种双重编号.

本脚本作用:
  1. 打开 .docx, 遍历所有段落
  2. 对 Heading 1/2/3 段落的 pPr, 强制 numId=0 (禁用 Word 自动编号)
  3. 同时, 如果文本里残留 "1. " / "1.1 " 等阿拉伯前缀, 也一并清理 (防御性)
  4. 写回原文件 (in-place)

用法:
  python fix_docx_headings.py <workspace>/02_<项目名>_详细设计文档.docx
  python fix_docx_headings.py --check <docx_path>     # 仅检查不修改
  python fix_docx_headings.py --batch <dir_glob>      # 批量处理

依赖:
  - python-docx (pip install python-docx)

退出码:
  0 = 成功 (无问题或已修复)
  1 = 文件不存在
  2 = 不是有效 .docx
  3 = python-docx 未安装
  4 = 修复过程中出错
"""
import argparse
import os
import re
import sys
import zipfile
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("[FAIL] python-docx 未安装. 安装: pip install python-docx")
    sys.exit(3)


# Word 中标准 Heading style name (中英文 template 都覆盖)
HEADING_STYLE_NAMES = {"Heading 1", "Heading 2", "Heading 3", "heading 1", "heading 2", "heading 3"}
HEADING_STYLE_IDS   = {"Heading1", "Heading2", "Heading3"}

# 防御性清理: 文本前缀里残留的阿拉伯数字编号模式
LEADING_NUM_PATTERNS = [
    re.compile(r"^\s*\d+(?:\.\d+){0,3}\.?\s+"),   # "1. ", "1.1 ", "1.1.1 ", "1.1.1.1 "
    re.compile(r"^\s*\d+(?:\.\d+){0,3}\t+"),       # "1\t", "1.1\t"
]


def is_valid_docx(p: Path) -> bool:
    if not p.exists() or p.stat().st_size < 1024:
        return False
    try:
        with zipfile.ZipFile(p) as z:
            return "word/document.xml" in z.namelist()
    except Exception:
        return False


def disable_auto_number(paragraph) -> bool:
    """
    在段落 pPr 上覆盖 numId=0, 禁用 Word 自动编号.
    返回: True 如果段落被修改
    """
    pPr = paragraph._p.get_or_add_pPr()
    modified = False
    for old in pPr.findall(qn("w:numPr")):
        pPr.remove(old)
        modified = True
    numPr = OxmlElement("w:numPr")
    ilvl  = OxmlElement("w:ilvl");  ilvl.set(qn("w:val"), "0")
    numId = OxmlElement("w:numId"); numId.set(qn("w:val"), "0")  # 0 = 不编号
    numPr.append(ilvl); numPr.append(numId)
    pPr.append(numPr)
    return True


def strip_leading_numbers(text: str) -> tuple:
    """
    清理段落文本里残留的 "1. " / "1.1 " 前缀.
    返回: (cleaned_text, was_modified)
    """
    original = text
    for pat in LEADING_NUM_PATTERNS:
        text = pat.sub("", text, count=1)
    return text, (text != original)


def is_heading_paragraph(p) -> bool:
    if p.style is None:
        return False
    name = (p.style.name or "").strip()
    if name in HEADING_STYLE_NAMES:
        return True
    if name in HEADING_STYLE_IDS:
        return True
    # fallback: 通过 styleId (e.g. "Heading1")
    style_id = None
    try:
        style_el = p.style.element
        style_id = style_el.get(qn("w:styleId"))
    except Exception:
        pass
    return style_id in HEADING_STYLE_IDS


def fix_one(docx_path: Path, check_only: bool = False) -> dict:
    """
    修复单个 .docx.
    返回 dict: { "headings": int, "numpr_stripped": int, "text_stripped": int, "modified": bool }
    """
    if not docx_path.exists():
        return {"error": f"文件不存在: {docx_path}"}
    if not is_valid_docx(docx_path):
        return {"error": f"不是有效 .docx: {docx_path}"}

    doc = Document(str(docx_path))
    stats = {
        "headings": 0,
        "numpr_stripped": 0,
        "text_stripped": 0,
        "modified": False,
    }

    for p in doc.paragraphs:
        if not is_heading_paragraph(p):
            continue
        stats["headings"] += 1
        if check_only:
            continue
        # 1. 强制 numId=0
        disable_auto_number(p)
        stats["numpr_stripped"] += 1
        # 2. 清理残留阿拉伯前缀
        new_text, changed = strip_leading_numbers(p.text)
        if changed:
            # python-docx 改 runs 比较麻烦, 直接整体替换首个 run 的 text
            # 保留第一个 run, 清空其他
            if p.runs:
                p.runs[0].text = new_text
                for r in p.runs[1:]:
                    r.text = ""
            stats["text_stripped"] += 1
        if True:
            stats["modified"] = True

    if not check_only and stats["modified"]:
        doc.save(str(docx_path))

    return stats


def main():
    ap = argparse.ArgumentParser(description="修复详细设计 .docx 标题双重编号 bug (software-factory 内置)")
    ap.add_argument("docx", nargs="?", help=".docx 文件路径")
    ap.add_argument("--check", action="store_true", help="仅检查, 不修改")
    ap.add_argument("--batch", help="glob 模式批量处理, e.g. '**/02_*详细设计*.docx'")
    ap.add_argument("--no-color", action="store_true", help="禁用彩色输出")
    args = ap.parse_args()

    if not args.docx and not args.batch:
        ap.print_help()
        sys.exit(0)

    targets = []
    if args.docx:
        targets.append(Path(args.docx))
    if args.batch:
        for p in Path(".").glob(args.batch):
            if p.suffix.lower() == ".docx":
                targets.append(p)

    total = {"files": 0, "headings": 0, "numpr_stripped": 0, "text_stripped": 0, "errors": 0}
    for t in targets:
        total["files"] += 1
        result = fix_one(t, check_only=args.check)
        if "error" in result:
            print(f"[FAIL] {t}: {result['error']}")
            total["errors"] += 1
            continue
        if args.check:
            print(f"[CHECK] {t}: 标题数={result['headings']}")
        else:
            print(f"[OK]   {t}: 标题={result['headings']}  numPr重置={result['numpr_stripped']}  文本清理={result['text_stripped']}")
        total["headings"]        += result["headings"]
        total["numpr_stripped"]  += result["numpr_stripped"]
        total["text_stripped"]   += result["text_stripped"]

    print()
    print(f"汇总: files={total['files']} headings={total['headings']} "
          f"numPr重置={total['numpr_stripped']} 文本清理={total['text_stripped']} errors={total['errors']}")
    sys.exit(0 if total["errors"] == 0 else 4)


if __name__ == "__main__":
    main()