#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_template.py - 首次安装后引导用户提供详细设计 .docx 模板

用法:
    python setup_template.py                     # 交互模式: 询问路径
    python setup_template.py --src <绝对路径>     # 直接指定
    python setup_template.py --check             # 仅检查 + 打印状态
    python setup_template.py --reset             # 删除已装的模板 (回到未装态)

行为:
    - 检查 $CODEX_HOME/skills/software-factory/templates/详细设计模板.docx 是否存在
    - 不存在: 询问用户输入源路径, 复制过去
    - 复制后做 SHA256 校验, 落到 phase0-template-setup.log

退出码:
    0 = 已就位 (无需动作或复制成功)
    1 = 用户取消或源文件不存在
    2 = 复制失败
"""
import argparse, hashlib, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
SKILL_DIR = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / "software-factory"
TPL_DST   = SKILL_DIR / "templates" / "详细设计模板.docx"
LOG_FILE  = SKILL_DIR / "phase0-template-setup.log"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_docx(p: Path) -> bool:
    """粗校验: ZIP 头 + 包含 word/document.xml"""
    if not p.exists() or p.stat().st_size < 1024:
        return False
    try:
        import zipfile
        with zipfile.ZipFile(p) as z:
            return "word/document.xml" in z.namelist()
    except Exception:
        return False


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def check() -> int:
    if TPL_DST.exists():
        size = TPL_DST.stat().st_size
        sha  = sha256(TPL_DST)
        valid = is_valid_docx(TPL_DST)
        print(f"✅ 模板已就位: {TPL_DST}")
        print(f"   size: {size} bytes")
        print(f"   sha256: {sha}")
        print(f"   valid docx: {valid}")
        return 0 if valid else 1
    else:
        print(f"❌ 模板缺失: {TPL_DST}")
        print(f"   请用: python setup_template.py --src <你的 .docx 路径>")
        return 1


def reset() -> int:
    if TPL_DST.exists():
        TPL_DST.unlink()
        log(f"reset: deleted {TPL_DST}")
        print(f"✅ 已删除 {TPL_DST}")
    else:
        print(f"ℹ️  模板本就不存在, 无需 reset")
    return 0


def install(src: str) -> int:
    src_path = Path(src)
    if not src_path.exists():
        print(f"❌ 源文件不存在: {src_path}")
        return 1
    if not is_valid_docx(src_path):
        print(f"❌ 源文件不是有效 .docx: {src_path}")
        return 1

    TPL_DST.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(src_path, TPL_DST)
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return 2

    size = TPL_DST.stat().st_size
    sha  = sha256(TPL_DST)
    log(f"installed: src={src_path} dst={TPL_DST} size={size} sha256={sha}")
    print(f"✅ 已复制到: {TPL_DST}")
    print(f"   size: {size} bytes")
    print(f"   sha256: {sha}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Setup 详细设计 .docx 模板 for software-factory skill")
    ap.add_argument("--src", help="源 .docx 文件绝对路径")
    ap.add_argument("--check", action="store_true", help="仅检查状态")
    ap.add_argument("--reset", action="store_true", help="删除已装模板")
    args = ap.parse_args()

    print(f"SKILL_DIR: {SKILL_DIR}")
    print(f"TPL_DST:   {TPL_DST}")
    print()

    if args.check:
        sys.exit(check())
    if args.reset:
        sys.exit(reset())
    if args.src:
        sys.exit(install(args.src))

    # 交互模式
    if TPL_DST.exists():
        print("模板已就位, 无需安装. 用 --reset 先删除可重新安装.")
        sys.exit(check())

    print("本 skill 需要一份 详细设计 .docx 模板作为样式基线.")
    print("它会从该模板继承 styles.xml / numbering.xml / theme1.xml / 封面样式.")
    print()
    print(f"目标: {TPL_DST}")
    print()
    print("请输入源 .docx 模板的绝对路径 (回车跳过则用 fallback 默认模板):")
    try:
        src = input("> ").strip().strip('"').strip("'")
    except EOFError:
        src = ""
    if not src:
        print("⚠️  跳过. Stage 2 将使用 docx skill 默认模板 (无公司样式).")
        sys.exit(1)
    sys.exit(install(src))


if __name__ == "__main__":
    main()