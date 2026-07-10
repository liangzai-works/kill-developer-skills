# prompts/architecture.md

> 用于 software-factory Stage 4 (含详细设计 / 架构 / 数据库) 的引导式 Prompt.
> v0.5.3: 恢复手写编号 "一. " / "1.1"; fix_docx_headings.py 仍强制调, 兜底关模板自动编号.

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
  1. 文档说明
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
- **v0.5.3 编号策略**: Heading 文本里**必须手写** "一、/" "1.1" 等中文 / 阿拉伯编号 (骨架 `templates/02_详细设计文档_九节骨架.md` 已经填好). 模板自带的自动编号会被 Step 1.5 的 fix_docx_headings.py 关掉, 单一来源 = 单一编号.

### Step 1.5 - ⚠️ 模板自动编号兜底关掉 (v0.5.1 起强制, v0.5.3 保留)

**问题**: 公司详细设计模板的 `styles.xml` 通常把 Heading 1/2/3 样式绑到 `numbering.xml` 的某个 `numId` (本仓库随附的模板就是 numId=5), Word 打开后会**自动**给段落加上 "1." "1.1" "1.1.1" 前缀.

**v0.5.1 退化症**: 我们曾走过 "删除手写编号 + 关自动编号" 这条路, 结果渲染出完全没有编号的标题 (用户在 taskmgr demo 上反馈 "标题的前面数字也没了").

**v0.5.3 修复**: 恢复手写编号 (骨架里重新有 `## 一、文档说明` / `### 1.1 内容概要`), 用 fix_docx_headings.py 关掉模板自动编号. 渲染 = 单一来源手写编号, 既不双重叠加, 也不会丢编号.

**根因 / 上下文**:

- 模板的 styles.xml 里: `<w:style w:type="paragraph" w:styleId="Heading1"><w:pPr><w:numPr><w:numId w:val="5"/><w:ilvl w:val="0"/></w:numPr></w:pPr>...</w:style>` — Heading 1/2/3 绑到 numId=5, Word 默认会给段落加 "1." / "1.1" 前缀.
- 我们的 9 节骨架 (`templates/02_详细设计文档_九节骨架.md`) 已经**手写**了中文 / 阿拉伯编号, 期望 Word 渲染就显示这套手写编号.
- 但模板的自动编号一旦保留, Word 会同时输出 "1." + "一、文档说明" → 又变回双重叠加. 因此 fix_docx_headings.py 必须把模板绑定的 numId 覆写为 0, 关掉自动编号.

**修复 (强制)**:

```bash
# docx skill 生成 .docx 之后, 强制调一次 fix_docx_headings.py
python skills/software-factory/scripts/fix_docx_headings.py \
  <项目名>工作空间/02_<项目名>_详细设计文档.docx
```

**该脚本会**:

1. 遍历 .docx 所有段落, 找出 Heading 1/2/3 段落
2. 强制把段落 pPr 的 numId 覆写为 0 (禁用 Word 自动编号)
3. 防御性清理文本里残留的 "1. " / "1.1 " / "1\t" 前缀 (防止之前流程误伤)
4. in-place 保存, 打印修改前后统计

**验收**:

- 重新打开修复后的 .docx
- Heading 1 应渲染成 "一、文档说明"  (无前缀数字 + 中文书名号)
- Heading 2 应渲染成 "1.1 内容概要"  (无前缀数字)
- 不会有 "1 一、文档说明" / "1.1 1.1 内容概要" 双重叠加
- 也不会出现 v0.5.1 退化症的完全无编号

**不允许**:

- ❌ 不调 `fix_docx_headings.py` 直接交付 .docx
- ❌ **v0.5.3 起**: 删掉骨架里的手写编号 (会变成 v0.5.1 退化症: 完全没编号)
- ❌ 手工逐段调用 `disable_auto_number(p)` (容易漏段, 不可靠)
- ❌ 删模板里 numbering.xml 的 numId (会破坏模板多级编号, 影响后续复用该模板的项目)

### Step 2.0 - 🆕 架构图自动生成 (v0.5.0 起强制, v0.5.1 强化业务模块)

> 这一步必须在写 `03_<项目名>_架构设计.md` **之前** 先做, 因为 PNG 是 Stage 2 (详细设计) 的"2. 总体设计"插图来源.

**0. 准备业务模块列表**: 从需求规格说明书里抽出业务模块 (例: 首页 / 节点管理 / 用户管理), 不要用技术分层.

**1. 调用 render_arch.py** (skill 内置脚本):

```bash
# 方式 A: 业务模块列表, 用 --layers 传 JSON 出占位 PNG
python skills/software-factory/scripts/render_arch.py \
  --layers '[["首页","概览仪表盘 + 关键指标"],["节点管理","节点注册 / 健康检查"],["用户管理","用户增删改查 / 角色权限"],["数据访问","JPA / Repository (DB 落地)"],["基础设施","Docker / 监控 (非业务模块, 备注用)"]]' \
  --out <项目名>工作空间/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"
```

**2. 然后写** `03_<项目名>_架构设计.md`, 至少含:

```markdown
# 03_<项目名>_架构设计

## 分层架构 (用于 render_arch.py 解析) — ⚠️ 此处填"业务模块", 不是 SpringBoot 技术分层

| 层 | 主要组件 |
|----|----------|
| 首页 | 概览仪表盘 + 关键指标 |
| 节点管理 | 节点注册 / 健康检查 |
| 用户管理 | 用户增删改查 / 角色权限 |
| 数据访问 | JPA / Repository (基础设施) |
```

**3. 调 render_arch.py 用 .md 重新出最终图** (覆盖占位 PNG):

```bash
python skills/software-factory/scripts/render_arch.py \
  --src <项目名>工作空间/03_<项目名>_架构设计.md \
  --out <项目名>工作空间/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"
```

**4. verify**: PNG 文件存在, size > 50KB. 不达标则:

- 调 `python scripts/render_arch.py --check` 看 matplotlib/字体是否就绪
- 失败回退: 在 `03_<项目名>_架构设计.md` 里写一段 ASCII 业务模块图 (作为 fallback)

**5. 嵌入详细设计**: Step 1 生成 `02_<项目名>_详细设计文档.docx` 时, 在 "2. 总体设计" 的 "2.1 架构图" 段插入这张 PNG (`docx skill` 嵌入图片能力).

### Step 2 - 架构设计 (Markdown, v0.5.1 强化业务模块)

**业务模块划分 (强约束, 禁止 SpringBoot 技术分层)**:

- ✅ **正确**: 按业务模块划分, 每个模块写清"问题描述 / 职责 / 入口 / 依赖"
  - 例: 首页 / 节点管理 / 用户管理 / 工单管理
- ❌ **错误**: 按 SpringBoot 技术分层罗列
  - 反例: controller / service / dao / repository / 表现层 / 业务层 / 持久层
  - 反例: 接入层 / 应用层 / 服务层 / 领域层 / 数据层 / 基础设施层
  - 反例: API 网关层 / 路由层 / 中间件层

**强制表格**:

```markdown
| 业务模块 | 问题描述 | 职责 | 入口 (URL/API) | 依赖 |
|----------|----------|------|----------------|------|
| 首页 | "用户登录后看到什么" | 概览 / 关键指标 / 快捷入口 | GET /api/dashboard | 节点服务 / 用户服务 |
| 节点管理 | "如何注册和监控节点" | 节点注册 / 健康检查 / 上下线 | POST /api/nodes | 数据访问 |
```

- 每个业务模块单独一行, "问题描述" 用一句话讲清"这模块解决什么业务问题"
- 即使是 demo 项目, 也必须至少列 2 个业务模块 (例: 首页 + 后台管理)
- 找不到业务模块说明分析不到位, 回去补 Phase 1 需求规格

**模块关系图 (业务模块架构图)**:

- 在 `03_<项目名>_架构设计.md` 的 "## 架构总览 (业务模块视图)" 段画 ASCII 或 mermaid
- 在 `03_<项目名>_架构图.png` 里画 PNG (按业务模块)
- 关系箭头 = 调用方向 / 数据流向, 不是部署拓扑

**其他 (保留旧版)**:

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
- ❌ 生成 Heading 段落不调 `scripts/fix_docx_headings.py` (双重编号 bug)
- ❌ **v0.5.3 起**: 删掉骨架里的手写编号 (会变成 v0.5.1 退化症: 完全没编号)
- 不写 SQL DDL 而只写 Markdown (后续 Stage 找不到入口)
- 🆕 **用临时脚本 (matplotlib / mermaid) 画架构图** — 必须用 skill 内置的 `scripts/render_arch.py`
- 🆕 跳 Step 2.0 直接出 .md — PNG 没生成, Stage 2 插图就缺
- 🆕 把架构图写成 ASCII 凑数 — 除非 render_arch.py 工具链缺失 (在 --check 失败时才允许)
- ❌ **v0.5.1**: 把架构图画成 SpringBoot 技术分层 (接入层 / 应用层 / 服务层 / 数据层 / 基础设施层)
- ❌ **v0.5.1**: 模块划分按 controller / service / dao 罗列
- ❌ **v0.5.1**: 业务模块没写"问题描述" (只写职责)

## 工具调用约定

- docx skill: 调 `skills/docx/SKILL.md` 实现 .docx 生成
- 模板读取: `python-docx` 或 Node `docx` 库均可
- 🆕 架构图: 必须 `python skills/software-factory/scripts/render_arch.py`, 不要再手画
- 🆕 标题修复: 必须 `python skills/software-factory/scripts/fix_docx_headings.py <docx>`, 不要再手写 disable_auto_number