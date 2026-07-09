# prompts/architecture.md

> 用于 software-factory Stage 4 (含详细设计 / 架构 / 数据库) 的引导式 Prompt.

## 你是谁

你是 software-factory 的架构师 / 详细设计作者.
负责同时产出三类文档.

## 输入

```yaml
project_name: "DEMO"
requirements: "01_<项目名>_需求规格说明书.md"
constraints:
  language: java 21
  framework: spring-boot 3.x
  database: sqlite | postgres | mysql
  ui: bootstrap 5 + vue 3 (CDN)
template_override: ""    # 可选, --template=<绝对路径>; 缺省按下面查找优先级
```

## 工作空间

- 根: `<项目名>工作空间/`
- 详细设计 .docx 模板查找 (4 级优先级 + fallback, 见 Step 1)
- 架构图: 见 Step 2.0 (调 scripts/render_arch.py)

## 输出 (4 个产物文件, 必给)

```
<项目名>工作空间/
├── 02_<项目名>_详细设计文档.docx     ⭐ 本 Stage 重点
├── 03_<项目名>_架构设计.md
├── 03_<项目名>_架构图.png            🆕 v0.5.0: 由 render_arch.py 自动生成
└── 04_<项目名>_数据库设计.md         (有 DB 时)
```

## 步骤

### Step 1 - 详细设计文档 (.docx, 必须)

**模板查找优先级** (从上往下, 命中即用):

1. **`--template=<绝对路径>` 参数** (用户显式指定, 优先级最高)
2. **`<项目名>工作空间/详细设计模板.docx`** (项目级覆盖, 用户可能为这个项目专门放了模板)
3. **`skills/software-factory/templates/详细设计模板.docx`** (skill 自带, 随 skill 一起发布)
   - 注: 此文件在 skill 仓库 .gitignore 内, 属于用户私有资产, 不会随仓库分发.
   - skill 安装到 `$CODEX_HOME/skills/software-factory/` 后若该文件缺失, 用户需自行从本地原始位置拷贝过去.
4. **fallback**: 调 docx skill 用其默认模板生成

**找到模板后**:

- 调 docx skill, 把该 .docx 作为样式基线 (styles.xml / numbering.xml / theme1.xml 直接复用)
- 按 9 节骨架填充内容:
  1. 概述
  2. 总体设计
  3. 模块设计
  4. 接口设计
  5. 数据库设计
  6. 界面设计
  7. 部署运行
  8. 错误处理
  9. 附录
- 输出: `02_<项目名>_详细设计文档.docx`
- 模板文件本身不参与文档内容, 只贡献样式 / 字体 / 标题级别 / 页眉页脚等

### Step 1.5 - ⚠️ 禁用模板自动编号 (关键, 不做会双重编号)

**问题**: 公司详细设计模板的 `styles.xml` 通常把 Heading 1/2/3 样式绑到 `numbering.xml` 的某个 `numId` (本仓库随附的模板就是 numId=5), Word 打开后会**自动**给段落加上 "1." "1.1" "1.1.1" 前缀.

**症状**: 生成的 .docx 打开看到 "1\t一、文档说明  1.1\t1.1 内容概要" 这种**双重编号**.

**根因**:
- 模板的 styles.xml 里: `<w:style w:type="paragraph" w:styleId="Heading1"><w:pPr><w:numPr><w:numId w:val="5"/><w:ilvl w:val="0"/></w:numPr></w:pPr>...</w:style>`
- python-docx `doc.add_paragraph(text, style="Heading 1")` 只是引用样式, 不复制样式属性, 所以段落会继承自动编号
- 我们又手动写了 "一、" "1.1" 文字, 结果 Word 渲染时 "1" + "一、文档说明" = "1  一、文档说明"

**修复** (生成脚本必须包含):

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def disable_auto_number(paragraph):
    """在该段落上覆盖 numId=0, 禁用 Word 自动编号"""
    pPr = paragraph._p.get_or_add_pPr()
    for old in pPr.findall(qn("w:numPr")):
        pPr.remove(old)
    numPr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0")
    numId = OxmlElement("w:numId"); numId.set(qn("w:val"), "0")  # 0 = 不编号
    numPr.append(ilvl); numPr.append(numId)
    pPr.append(numPr)

# 在每个 Heading 1/2/3 段落 add 后立即调用
for p in doc.paragraphs:
    if p.style and p.style.name in ("Heading 1","Heading 2","Heading 3"):
        disable_auto_number(p)
```

**验收**: 生成的 .docx 重新打开, Heading 段落前不再有 "1." / "1.1" 自动编号, 只有我们写的 "一、" / "1.1" 文字.

### Step 2.0 - 🆕 架构图自动生成 (v0.5.0 起强制)

> 这一步必须在写 `03_<项目名>_架构设计.md` **之前** 先做, 因为 PNG 是 Stage 2 (详细设计) 的"2. 总体设计"插图来源.

**0. 调用 render_arch.py** (skill 内置脚本):

```bash
# 方式 A: 先粗列层, 用 --layers 传 JSON 出占位 PNG
python skills/software-factory/scripts/render_arch.py \
  --layers '[["接入层","Nginx / SLB"],["应用层","Spring Boot 3.x + Vue 3"],["服务层","工作台 / 节点管理 / 应用管理"],["数据层","MySQL 8.0"],["基础设施","Docker / 监控"]]' \
  --out <项目名>工作空间/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"
```

**1. 然后写** `03_<项目名>_架构设计.md`, 至少含:

```markdown
# 03_<项目名>_架构设计

## 分层架构 (用于 render_arch.py 解析)

| 层 | 主要组件 |
|----|----------|
| 接入层 | Nginx / SLB |
| 应用层 | Spring Boot 3.x / Vue 3 |
| 服务层 | 工作台 / 节点管理 / 应用管理 |
| 数据层 | MySQL 8.0 / Redis |
| 基础设施 | Docker / 监控 |
```

(可用表格或 `## 层名` + 子项两种格式, render_arch.py 都认)

**2. 调 render_arch.py 用 .md 重新出最终图** (覆盖占位 PNG):

```bash
python skills/software-factory/scripts/render_arch.py \
  --src <项目名>工作空间/03_<项目名>_架构设计.md \
  --out <项目名>工作空间/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"
```

**3. verify**: PNG 文件存在, size > 50KB. 不达标则:

- 调 `python scripts/render_arch.py --check` 看 matplotlib/字体是否就绪
- 失败回退: 在 `03_<项目名>_架构设计.md` 里写一段 ASCII 分层图 (作为 fallback)

**4. 嵌入详细设计**: Step 1 生成 `02_<项目名>_详细设计文档.docx` 时, 在 "2. 总体设计" 或 "3. 模块设计" 段插入这张 PNG (`docx skill` 嵌入图片能力).

### Step 2 - 架构设计 (Markdown)

- 业务模块划分 (按业务, 不按 SpringBoot 技术分层)
  - 例: 首页 / 节点管理 / 用户管理, 不是 controller/service/dao
- 时序图 (mermaid / ascii, 复杂流程用 mermaid)
- 技术栈表 + 端口 / 路径约定
- API 列表 (在 Step 1 的 .docx "4. 接口设计" 里展开)

### Step 3 - 数据库设计

- 实体清单 + 字段
- 完整 SQL DDL (存到 `源代码/<项目名>-server/src/main/resources/schema.sql`)
- Markdown 摘要到 `04_<项目名>_数据库设计.md`

## 不允许做的事

- 跳过任一产物文件 (即使很简单也必须落)
- 不阅读 .docx 模板就直接生成 (会失去样式基线)
- 把模板文件复制进 `<项目名>工作空间/` (污染产物目录)
- 把模板文件提交到 skill 仓库 (.gitignore 已排除)
- 生成 Heading 段落后**忘记调 disable_auto_number** (双重编号 bug)
- 不写 SQL DDL 而只写 Markdown (后续 Stage 找不到入口)
- 🆕 **用临时脚本 (matplotlib / mermaid) 画架构图** — 必须用 skill 内置的 `scripts/render_arch.py`
- 🆕 跳 Step 2.0 直接出 .md — PNG 没生成, Stage 2 插图就缺
- 🆕 把架构图写成 ASCII 凑数 — 除非 render_arch.py 工具链缺失 (在 --check 失败时才允许)

## 工具调用约定

- docx skill: 调 `skills/docx/SKILL.md` 实现 .docx 生成
- 模板读取: `python-docx` 或 Node `docx` 库均可
- 🆕 架构图: 必须 `python skills/software-factory/scripts/render_arch.py`, 不要再手画