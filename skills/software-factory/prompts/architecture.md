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
- 详细设计 .docx 模板查找 (3 级优先级 + fallback, 见 Step 1)

## 输出 (3 个产物文件, 必给)

```
<项目名>工作空间/
├── 02_<项目名>_详细设计文档.docx     ⭐ 本 Stage 重点
├── 03_<项目名>_架构设计.md
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

**注意**:

- 不要把模板拷贝到生成产物目录 (它是 skill 资源, 不是项目产物)
- 若模板缺失但用户希望使用, 应先询问用户:
  > "未在工作空间 / skill 目录找到 `详细设计模板.docx`, 是否提供绝对路径? 留空则用 docx skill 默认模板."

### Step 2 - 架构设计 (Markdown)

- 模块划分 + 时序图 (mermaid / ascii)
- 技术栈表 + 端口 / 路径约定
- API 列表

### Step 3 - 数据库设计

- 实体清单 + 字段
- 完整 SQL DDL (存到 `源代码/<项目名>-server/src/main/resources/schema.sql`)
- Markdown 摘要到 `04_<项目名>_数据库设计.md`

## 不允许做的事

- 跳过任一产物文件 (即使很简单也必须落)
- 不阅读 .docx 模板就直接生成 (会失去样式基线)
- 把模板文件复制进 `<项目名>工作空间/` (污染产物目录)
- 把模板文件提交到 skill 仓库 (.gitignore 已排除)
- 不写 SQL DDL 而只写 Markdown (后续 Stage 找不到入口)

## 工具调用约定

- docx skill: 调 `skills/docx/SKILL.md` 实现 .docx 生成
- 模板读取: `python-docx` 或 Node `docx` 库均可