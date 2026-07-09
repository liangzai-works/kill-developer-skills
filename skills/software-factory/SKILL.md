---
name: software-factory
description: |
  元技能 - 软件工厂工作流编排器。
  按 Phase 0/1/2 流水线, 产出 NN_<项目名>_<文档名>.<ext> 系列文档与可运行代码。
  详细设计文档会按 4 级优先级读取 "详细设计模板.docx" 作为样式基线 (若无则 fallback)。
  生成 Heading 段落时会禁用模板自带的自动编号 (避免与手写编号双重叠加)。
  所有过程文件集中在 <项目名>工作空间/ 一个目录内, 数字前缀表示阶段序号。
version: 0.4.0
type: meta
---

# 软件工厂 (Software Factory)

> 把一段需求, 端到端变成: 文档 + 可运行软件 + 验证 + 交付。
> 所有产物命名遵循 `NN_<项目名>_<文档名>.<ext>`。

## 1. 它做什么

`software-factory` 是元技能本身不写代码, 编排能力调用其他 Skill 完成。
按阶段产出可读、可追溯、可复盘的产物。

## 2. 不做什么

- 不重写已有 Skill 能力
- 不在用户没授权时擅自做技术决策
- 不为节省 token 跳过阶段 (token 紧张时压缩, 不跳过)
- 不把模板文件当产物推进 git / 复制到项目工作空间
- 不在 Heading 段落上保留模板的自动编号 (会导致与手写编号双重叠加)

## 3. 输入

```yaml
user_input:
  text: "项目需求原文"             # 必填
  project_name: "可选, 若缺省从原文首句主题词取"
  workspace_dir: "DEMO工作空间/"  # 缺省按 "<项目名>工作空间/" 建
  template: "可选, --template=<绝对路径> 显式指定详细设计模板"
```

## 4. 工作空间结构

```
<项目名>工作空间/
├── 01_<项目名>_需求规格说明书.md
├── 02_<项目名>_详细设计文档.docx     (样式基线见 §5)
├── 03_<项目名>_架构设计.md            (架构图/部署图/时序图)
├── 04_<项目名>_数据库设计.md          (有数据库时)
├── 04b_<项目名>_UI设计.md             (含前端项目)
├── 源代码/
│   ├── <项目名>-server/      (后端)
│   └── <项目名>-web/         (前端)
├── 05_<项目名>_测试报告.md
├── 06_<项目名>_验收报告.md
├── 07_<项目名>_交付报告.md
└── screenshots/
    └── <NN>-<含义>.png
```

**命名约束**:

- `NN` 两位数字前缀, 从 01 起, 表示阶段序号
- `<项目名>` 全大写或驼峰一致, 与 workspace 目录名拼写相同
- 文档名中文, 用 _ 分隔
- 扩展名用文档本应格式 (md / docx / sql / png / 等)

## 5. 详细设计模板查找 (4 级优先级 + fallback)

> 注意: `<项目名>工作空间/` 是 **生成产物目录**, 不放模板。模板是 **skill 自己的资源**。

| 优先级 | 位置                                                  | 说明                                          |
|--------|-------------------------------------------------------|-----------------------------------------------|
| 1      | `--template=<绝对路径>` 显式传入                      | 用户最高优先级                                |
| 2      | `<项目名>工作空间/详细设计模板.docx`                  | 项目级覆盖 (用户为这个项目专门放一份)         |
| 3      | `skills/software-factory/templates/详细设计模板.docx` | skill 自带, 随 skill 安装到 `$CODEX_HOME/skills/` |
| 4      | fallback                                              | docx skill 默认模板                           |

**重要**:

- 调用 `docx` Skill 完成 .docx 生成 (本元技能不自造 Word)
- 命中 1/2/3 时, 模板作为 **样式基线** (styles.xml / numbering.xml / theme1.xml 直接复用)
- 模板本身是 **用户私有资产**, 在 skill 仓库 `.gitignore` 内, **不会随仓库分发**
- skill 安装到 `$CODEX_HOME/skills/` 后若该文件缺失, 提示用户提供绝对路径

## 5.1 首次安装后的模板准备 (重要)

skill 仓库**故意不**带 `templates/详细设计模板.docx` (用户私有资产, gitignore 排除). 因此:

**首次 `$software-factory` 执行 Stage 2 之前**, skill 应:

1. 检查 `$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx` 是否存在
2. 若不存在, 询问用户:
   > "本 skill 用公司详细设计模板作为样式基线. 请提供 .docx 模板的绝对路径
   > (回车跳过则用 docx skill 默认模板, 但会失去 CEC 封面/标题样式)."
3. 收到路径后, 复制到 `$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx`
4. 记录此次复制到 `phase0-template-setup.log` 备查

**已安装示例**: 当前仓库 `C:\work\skills-workspace\kill-developer-skills\skills\software-factory\templates\详细设计模板.docx` 已通过开发期手动复制到位 (442KB, 9 节 + CEC 封面).

## 5.2 ⚠️ 模板自动编号陷阱 (v0.4.0 必修)

公司详细设计模板的 `styles.xml` 通常把 Heading 1/2/3 绑到 `numbering.xml` 的某个 numId, Word 会**自动**给段落加 "1." "1.1" "1.1.1" 前缀. 如果我们又手动写了 "一、" "1.1" 文字, 会出现**双重编号**.

**症状**: 生成的 .docx 打开看到 "1\t一、文档说明  1.1\t1.1 内容概要"

**根因**:
- 模板 `styles.xml`: `<w:style w:type="paragraph" w:styleId="Heading1"><w:pPr><w:numPr><w:numId w:val="5"/><w:ilvl w:val="0"/></w:numPr></w:pPr>...</w:style>`
- python-docx `add_paragraph(text, style="Heading 1")` 只引用样式, 段落继承自动编号

**修复** (写在 `prompts/architecture.md` Step 1.5): 在每个 Heading 段落上设 `numId=0` 关闭自动编号, 只保留手写文字.

## 6. 工作流 (Phase)

### Phase 0 - 技能环境准备

- 比对 skill-manifest 与已装 Skills
- 缺失项走 install_mode (interactive / auto)
- **新增**: 检查 `templates/详细设计模板.docx` 是否就位, 没有就走 §5.1 setup

### Phase 1 - 需求评估

- 识别 Idea / Spec 模式
- 输出 `01_<项目名>_需求规格说明书.md`
- 缺失项列 `01_<项目名>_需求假设清单.md` (待用户确认)

### Phase 2 - 8 Stage 流水线

| 序号 | 名称 | 必选 | 产出 (在工作空间根) |
|------|------|------|----------------------|
| 1 | 需求规格 | ✅ | 01_<项目名>_需求规格说明书.md |
| 2 | 详细设计 | ✅ | 02_<项目名>_详细设计文档.docx (按 §5 优先级找模板, 见 §5.2 禁用自动编号) |
| 3 | 架构设计 | ✅ | 03_<项目名>_架构设计.md |
| 4 | 数据库设计 | 数据库型必选 | 04_<项目名>_数据库设计.md (含 .sql) |
| 5 | UI 设计 | 前端型必选 | 04b_<项目名>_UI设计.md + 源代码/<项目名>-web/prototype.html |
| 6 | 实现 | ✅ | 源代码/<项目名>-server/ 与源代码/<项目名>-web/ |
| 7 | 构建运行 | ✅ | runtime.log + health-check.json |
| 8 | 浏览器验收 | ✅ (前端型) | 06_<项目名>_验收报告.md + screenshots/*.png |
| 9 | 测试评审 | ✅ | 05_<项目名>_测试报告.md + 08_<项目名>_代码评审报告.md |

> 前端型项目永远不缺 Stage 8 - 即使 hello world, 也要落浏览器验收报告与截图。

## 7. 强制 UI Artifact 规则 (v0.3.0 继承)

任何含有前端 UI 的项目都必须落 UI design artifact:

- 进入 Stage 5 (UI Design) 时, 读取 prompt 强制条款, 生成至少 1 个 HTML 原型 + CSS 变量
- 不允许 skip_when
- token 紧张时, 压缩原型 (单页 + 状态 tab) 而非 skip

## 8. 控制

- pause / resume / rerun_stage 同上
- dry-run: 只到 Phase 1

## 9. 触发方式

```
$software-factory 开发一个简单的留言板
$software-factory --project=DEMO
$software-factory --template=D:/company/详细设计模板.docx
$software-factory --rerun=stage2
```

## 10. v0.4.0 变更日志

- v0.4.0: 修复模板自动编号双重叠加 bug
  - `prompts/architecture.md` 新增 Step 1.5: 强制 `disable_auto_number(p)` 把 numId=0
  - `SKILL.md` §5.2 文档化症状 / 根因 / 修复
  - `SKILL.md` §5.1 文档化首次安装后模板准备流程
- v0.3.0: 修复详细设计模板查找路径 (4 级优先级 + `--template=`)
- v0.2.0: NN_<项目名>_<文档名> 命名约定 + 单工作空间目录 + 中文文件名
- v0.1.0: 初始 scaffold