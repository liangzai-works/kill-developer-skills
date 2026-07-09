# 详细设计模板放在哪里 (WHERE_TEMPLATE)

> software-factory skill 找详细设计 .docx 模板的规则
> 适用: v0.4.0+, 阅读时间 2 分钟

## 一句话

把模板放这里：

```
$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx
```

Windows 等价路径: `C:\Users\<你>\.codex\skills\software-factory\templates\详细设计模板.docx`

放好后, skill 跑 Stage 2 时会自动用这个模板做样式基线, 不会 fallback 到 docx 默认模板.

## 4 级查找优先级

skill 在 Stage 2 阶段按下面顺序找模板, **找到就停**:

| 优先级 | 位置                                                | 何时用                                |
|--------|-----------------------------------------------------|---------------------------------------|
| 1      | `--template=<绝对路径>` 启动参数                    | 想覆盖时显式传                        |
| 2      | `<项目名>工作空间/详细设计模板.docx`                | 这个项目专门准备的模板                |
| 3      | `$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx` | **默认放这里, skill 装好后用一次** |
| 4      | (docx skill 默认模板)                              | 啥都没有时的兜底, 无公司样式          |

## 三种"放进优先级 3"的方式

### 方式 A: 交互式 (推荐新手)

```bash
python $CODEX_HOME/skills/software-factory/scripts/setup_template.py
```

脚本会问你源文件路径, 然后自动复制到 `templates/详细设计模板.docx`.

### 方式 B: 命令行指定

```bash
python setup_template.py --src D:\我的文档\详细设计模板.docx
```

### 方式 C: 手动 copy

```bash
# Windows PowerShell
Copy-Item D:\我的文档\详细设计模板.docx `
  $env:USERPROFILE\.codex\skills\software-factory\templates\详细设计模板.docx

# Linux / macOS
cp /path/to/详细设计模板.docx \
   ~/.codex/skills/software-factory/templates/
```

## 验证是否就位

```bash
python $CODEX_HOME/skills/software-factory/scripts/setup_template.py --check
```

期望输出:

```
SKILL_DIR: C:\Users\<你>\.codex\skills\software-factory
TPL_DST:   C:\Users\<你>\.codex\skills\software-factory\templates\详细设计模板.docx

[OK] template ready: ...
   size: 442037 bytes
   sha256: ...
   valid docx: True
```

## 模板文件为什么不在 GitHub 仓库里

- `.gitignore` 排除了 `skills/**/templates/详细设计模板.docx`
- 原因: 模板通常是公司私有资产 (含品牌样式 / 内部规范)
- skill 装好后模板要**自己提供**, 不会随仓库分发

## 常见问题

### Q1: 装好 skill 后, 我没复制模板, 直接跑会怎样?

Stage 2 会走优先级 4 (docx skill 默认模板), 生成的 .docx 不会有公司样式, 文件也小 (10KB 左右). 你会看到提示:

> "本 skill 用公司详细设计模板作为样式基线. 请提供 .docx 模板的绝对路径 (回车跳过则用 docx skill 默认模板)"

### Q2: 模板是公司发的, 我能 push 到自己 fork 吗?

可以, 但建议**只在自己的 fork 里覆盖 .gitignore**, 不影响主仓:

```bash
# 在 fork 仓里
git config --local --add include.path ../.gitconfig
echo '!skills/**/templates/详细设计模板.docx' > .gitignore.local
git add -f skills/software-factory/templates/详细设计模板.docx
```

或者更简单: 在 fork 仓里**临时**改 `.gitignore` 加 `!` 取消排除, push 后再改回去.

### Q3: 多个项目用不同模板?

用优先级 2: 把项目模板放 `<项目名>工作空间/详细设计模板.docx`, 覆盖 skill 默认.

### Q4: 升级 skill 后模板会被覆盖吗?

不会. `setup_template.py` 复制到 `templates/` 后, 后续 `Copy-Item` reinstall 只覆盖 `prompts/` `SKILL.md` `workflow.yaml` `skill-manifest.yaml` `scripts/`, **不会动 `templates/` 下的文件**.

### Q5: 模板失效了 (修改时间 / SHA256 变了) 怎么办?

```bash
# 重新检查
python setup_template.py --check

# 强制重装
python setup_template.py --src /path/to/new/template.docx

# 或者用 --reset 清掉再装
python setup_template.py --reset
python setup_template.py --src /path/to/new/template.docx
```