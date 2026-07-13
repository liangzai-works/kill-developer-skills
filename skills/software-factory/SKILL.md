---
name: software-factory
description: |
  元技能 - 软件工厂工作流编排器。 按 Phase 0/1/2 流水线， 产出 NN_<项目名>_<文档名>.<ext> 系列文档与可运行代码。 详细设计文档会按 4 级优先级读取 "详细设计模板.docx" 作为样式基线 (若无则 fallback)。 文档生成后强制调用内置 scripts/fix_docx_headings.py 一刀切修复 Heading 双重编号 (模板自动编号 + 手写编号叠加)。 内置 scripts/render_arch.py 一键生成系统架构图 (PNG) 并嵌入详细设计文档， 架构图强制按业务模块维度绘制 (SpringBoot 技术分层视为反例并禁止)。 9 节骨架保留 一、 / 1.1 手写编号, 文档生成后内置 scripts/fix_docx_headings.py 一刀切关掉模板自动编号, 避免双重叠加且保留中文编号。 所有过程文件集中在 <项目名>工作空间/ 一个目录内, 数字前缀表示阶段序号。
version: 0.6.0
type: meta
---

# 软件工厂 (Software Factory)

> 把一段需求 端到端变成 文档 + 可运行软件 + 验证 + 交付。
> 所有产物命名遵循 `NN_<项目名>_<文档名>.<ext>`。

## 1. 它做什么
`software-factory` 是元技能本身不写代码, 编排能力调用其他 Skill 完成。 按阶段产出可读、可盘、可复盘的产物。

## 2. 不做什么
- 不重写已有 Skill 能力
- v0.5.4 起: **不要在 Stage 8 用下面这些看着像但实际坏的 iab API**:
  - `tab.screenshot({path})` (CDP Page.captureScreenshot 长时间 hang 在 Statsig analytics)
  - `tab.content.export()` (iab 抛 `Codex in-app browser does not support command`)
  - `tab.playwright.evaluate(...)` (永远返回 undefined, 不论返回什么类型)
  - `tab.playwright.domSnapshot()` (抛 `incrementalAriaSnapshot is not a function`)
  - 必须走 `tab.dom_cua.get_visible_dom()` 拿 node_id → `tab.dom_cua.click({node_id})` /`tab.dom_cua.type({text})`
  - 落盘截图用本地 headless chrome 兜底 (server 进程拿不到 iab 截图)
- 不在用户未授权时擅自做技术决策
- 不为节省 token 跳过阶段 (token 紧张时压缩, 不跳)
- 不把模板文件当作产物推 git / 复制到项目工作空间
- 不在没有调 `scripts/fix_docx_headings.py` 的情况下交付 .docx (会导致 Heading 双重编号)
- 不在 Heading 文本里手写 "一、" / "1.1" (会导致双重编号)
- 不把架构图按 SpringBoot 技术分层绘制 (接入层 / 应用层 / 服务层 / 数据层 / 基础设施层 等禁止作为主层)
- 不把"模块划分"按 controller / service / dao / repository 罗列 (必须是业务模块维度)
- 不跳过 Codex 右侧 in-app browser 面板 (v0.5.2 起, 浏览器验收默认要打开这个面板)

## 3. 输入

```yaml
user_input:
  text: "项目需求原文"             # 必填
  project_name: "可选, 若缺省从原文首句主题提取"
  workspace_dir: "DEMO工作空间/"  # 缺省按 "<项目名>工作空间/" 建
  template: "可选, --template=<绝对路径> 显式指定详细设计模板"
```

## 4. 工作空间结构

```
<项目名>工作空间/
├── 01_<项目名>_需求规格说明书.md
├── 02_<项目名>_详细设计文档.docx     (样式基线见搂5, 标题修复见搂5.2)
├── 03_<项目名>_架构设计.md            (按业务模块维度, 见搂5.3)
├── 03_<项目名>_架构图.png            (架构图自动生成, 见搂5.3)
├── 04_<项目名>_数据库设计.md          (有数据库时)
├── 04_<项目名>_建库脚本.sql
├── 04b_<项目名>_UI设计.md             (含前端项目)
├── 05_<项目名>_测试报告.md
├── 06_<项目名>_验收报告.md
├── 07_<项目名>_交付报告.md
└── 源代码/
    ├── <项目名>-server/      (后端)
    └── <项目名>-web/         (前端)
└── screenshots/
    └── <NN>-<语义>.png
```

**命名约束**:

- `NN` 两位数字前缀, 从 01 起, 表示阶段序号
- `<项目名>` 全大写或拼写一致, 与 workspace 目录名拼写相同
- 文档名中间用 `_` 分隔
- 扩展名用文档本应格式 (md / docx / sql / png / 等)

## 5. 详细设计模板查找 (4 级优先级 + fallback)

> 注意: `<项目名>工作空间/` 是**生成产物目录**, 不放模板。 模板是 **skill 自己的资源**。

| 优先级 | 位置                                                  | 说明                                          |
|--------|-------------------------------------------------------|-----------------------------------------------|
| 1      | `--template=<绝对路径>` 启动参数                      | 用户最高优先级                                |
| 2      | `<项目名>工作空间/详细设计模板.docx`                  | 项目级覆盖 (用户为这个项目专门放一份)         |
| 3      | `skills/software-factory/templates/详细设计模板.docx` | skill 自带, 随 skill 安装到 `$CODEX_HOME/skills/` |
| 4      | fallback                                              | docx skill 默认模板                           |

**重要**:

- 调用 `docx` Skill 完成 .docx 生成 (本元技能不自写 Word)
- 命中 1/2/3 时, 模板作为 **样式基线** (styles.xml / numbering.xml / theme1.xml 直接复用)
- 模板本身是**用户私有资产**, 在 skill 仓库 `.gitignore` 排, **不会随仓库分发**
- skill 安装到 `$CODEX_HOME/skills/` 后若该文件缺失, 提示用户提供绝对路径

## 5.1 首次安装后的模板准备 (重要)

skill 仓库不携带详细设计模板 .docx (避免泄漏公司内部样式 + 控制仓库体积)。 首次安装后必须手动放入 `$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx`, 否则详细设计会回退到 docx skill 默认模板 (无公司样式, 文件偏小)。

**准备步骤**:

1. 找到公司现有的"详细设计模板.docx" (一般在内网知识库/团队文档里能找到)
2. 文件名必须严格是 `详细设计模板.docx`, 包含"封面/标题样式/正文样式"等必备元素
3. 拿到路径后, 复制到 `$CODEX_HOME/skills/software-factory/templates/详细设计模板.docx`
4. 记录此次复制到 `phase0-template-setup.log` 备查

**已安装示意**: 当前仓库 `C:\work\skills-workspace\kill-developer-skills\skills\software-factory\templates\详细设计模板.docx` 已通过开发期手动复制到位 (442KB, 9 节 + 公司品牌封面)。

## 5.2 ⚠️ Heading 双重编号: 强制调用 fix_docx_headings.py (v0.5.1 强约束)

**症状**: 详细设计 .docx 打开后看到 "1	文档说明  1.1	1.1 内容概要" 这种双重编号.

**根因**:
- 公司详细设计模板的 `styles.xml` 把 Heading 1/2/3 样式绑到 `numbering.xml` 的某个 `numId` (仓库随附的模板就是 numId=5), Word 打开后**自动**给段落加 "1." "1.1" "1.1.1"
- 如果我们又在 Heading 文本里手写 "一." / "1.1" / "1. ", Word 渲染时两个编号源叠加 → 双重编号

**修复 (强约束)**: docx skill 产出 .docx **之后, 交付之前**, **必须**调用:

```bash
python skills/software-factory/scripts/fix_docx_headings.py \
  <项目名>工作空间/02_<项目名>_详细设计文档.docx
```

该脚本是 skill 内置能力, 在 `scripts/fix_docx_headings.py` (~6.7KB, 仅依赖 `python-docx`):

- 遍历 .docx 所有 Heading 1/2/3 段落
- 强制把段落 pPr 的 `numId` 覆写为 0 (禁用 Word 自动编号)
- 防御性清理文本里残留的 "1. " / "1.1 " / "1\t" 前缀
- in-place 保存, 打印修改前后统计

**不允许**:

- ❌ 不调 `fix_docx_headings.py` 直接交付 .docx
- ❌ 在 9 节骨架文本里手写 "一、" "1.1" 等 (Step 1 已经把骨架改为不带手写编号)
- ❌ 手工逐段调用 `disable_auto_number(p)` (容易漏段, 不可靠)
- ❌ 删模板里 numbering.xml 的 numId (会破坏模板多级编号, 影响后续复用该模板的项目)

**验收**:

```bash
python scripts/fix_docx_headings.py --check <workspace>/02_<项目名>_详细设计文档.docx
# 期望: 标题数=N (每个 Heading 都列出来了), 不应有未修复的双重编号
```

## 5.3 ⚠️ 架构图自动生成 (v0.5.0 起强制, v0.5.1 强化业务模块)

详细设计文档里需要"系统架构图". 之前靠手画或 ASCII 凑数, 现在用内置 `scripts/render_arch.py` 一键生成 PNG, 再嵌入 .docx.

**强制业务模块维度 (v0.5.1)**:

- ✅ **正确**: 按业务模块划分 (例: 首页 / 节点管理 / 用户管理), 每模块写"问题描述 + 职责 + 入口 + 依赖"
- ❌ **错误 (SpringBoot 技术分层)**: 接入层 / 表现层 / 路由层 / API 网关层 / 应用层 / 服务层 / 领域层 / 持久层 / 数据访问层 / 数据层 / 基础设施层
- ❌ **错误 (按技术组件)**: Controller / Service / Repository / DAO / 中间件层

**调用方式**:

```bash
# 方式 1: 从 Markdown 架构描述文件解析 (推荐)
python scripts/render_arch.py \
  --src <workspace>/03_<项目名>_架构设计.md \
  --out <workspace>/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"

# 方式 2: 直接传业务模块 JSON
python scripts/render_arch.py \
  --layers '[["首页","概览仪表盘 / 关键指标"],["节点管理","节点注册 / 健康检查"],["用户管理","增删改查 / 角色权限"],["数据访问","Repository / DB 落地"],["基础设施","Docker / 监控 (备注)"]]' \
  --out <workspace>/03_<项目名>_架构图.png \
  --title "<项目名> 系统架构图"

# 检查环境依赖
python scripts/render_arch.py --check
```

**特性**:

- 输入支持 3 种: `.md` (表格或标题列表) / `.json` / `--layers=` JSON
- 中文字体 fallback: SimHei → Microsoft YaHei → PingFang SC → Arial Unicode MS → DejaVu Sans
- 离线运行, 不依赖网络
- 默认 fallback 也是业务模块示例 (非技术分层), v0.5.1 起改了

**何时调用**: Stage 3 (架构设计) 产出 `03_<项目名>_架构设计.md` 之后, **必须**调用 `render_arch.py` 生成 `03_<项目名>_架构图.png`. 该 PNG 在 Stage 2 (详细设计) 的"2. 总体设计"或"3. 模块设计"里作为插图嵌入.

**重要**:

- 若架构复杂 (微服务/多集群/数据流), ASCII mermaid 仍可用作补充, 但分层架构主图必须用 `render_arch.py` 出的 PNG
- PNG 内容按"业务模块"绘制, 不是按 SpringBoot 技术分层 (提交/评审会被打回)
- 即使是 hello demo, 也至少 2 个业务模块 (例: 首页 + 后台), 不允许空架构图

## 6. 工作流 (Phase)

### Phase 0 - 技能环境准备
- 比对 skill-manifest 与已装 Skills
- 缺失项走 install_mode (interactive / auto)
- 检查 `templates/详细设计模板.docx` 是否就位, 没有就走 搂5.1 setup

### Phase 1 - 需求评估
- 识别 Idea / Spec 模式
- 输出 `01_<项目名>_需求规格说明书.md`
- **v0.5.1 新增**: 需求规格里必须抽出"业务模块"清单, 作为 Stage 3 模块划分的依据

### Phase 2 - 9 Stage 流水线
| 序号 | 名称 | 必需? | 产出 (在工作空间根) |
|------|------|------|----------------------|
| 1 | 需求规格 | ✓ | 01_<项目名>_需求规格说明书.md (含业务模块列表) |
| 2 | 详细设计 | ✓ | 02_<项目名>_详细设计文档.docx (按 搂5 优先级找模板, 含架构图, 走 搂5.2 调 fix_docx_headings.py 禁自动编号) |
| 3 | 架构设计 | ✓ | 03_<项目名>_架构设计.md (按业务模块) + **03_<项目名>_架构图.png** (走 搂5.3 调 render_arch.py) |
| 4 | 数据库设计 | 数据库型必需? | 04_<项目名>_数据库设计.md + 04_<项目名>_建库脚本.sql |
| 5 | UI 设计 | 前端型必需? | 04b_<项目名>_UI设计.md + 源代码/<项目名>-web/prototype.html |
| 6 | 实现 | ✓ | 源代码/<项目名>-server/ 与源代码/<项目名>-web/ |
| 7 | 构建运行 | ✓ | runtime.log + health-check.json |
| 8 | 浏览器验收 | ✓ (前端型) | 06_<项目名>_验收报告.md + screenshots/*.png (v0.5.2 强制开右侧 in-app browser 面板) |
| 9 | 测试评审 | ✓ | 05_<项目名>_测试报告.md + 08_<项目名>_代码评审报告.md |

> 前端型项目永远不跳 Stage 8 - 即使 hello world, 也要塞浏览器验收报告与截图。`n> **v0.5.2 起**: Stage 8 还必须打开 Codex 右侧 in-app browser 面板, 用户实时看到测试过程 (见搂6 / workflow.yaml Stage 8 / prompts/review.md).

## 6.5 外部 Skill 注入点 (v0.6.0 新增)

在原有 Phase / Stage 流水线之上, 预留两处外部 Skill 注入点. 详见 `skill-manifest.yaml#workflows[software-factory].required-skills`.

### 6.5.1 需求阶段: pm-review-board

- **触发位置**: `phase1.review` (在 `phase1.spec` 写出 `01_<项目名>_需求规格说明书.md` 之后, Phase 2 启动之前)
- **职责**: 对刚生成的 PRD 走 6 角色并行评审 (产品 / 研发 / 测试 / 设计 / 运营 / 法务)
- **输入**: `01_<项目名>_需求规格说明书.md`
- **输出**: `01_<项目名>_需求评审记录.md` (沿用 pm-review-board 输出格式)
- **安装**: `$skill-installer --repo hexi664/pm-review-board --path . --name pm-review-board`
- **门禁**:
  - ✅ 通过 / ⚠️ 有条件通过 → 评审记录作为附件进入 Phase 2
  - ❌ 不通过 → 阻断项回写到 spec.md "待澄清问题", retry(1) `phase1.spec`
- **备注**: 仓库 `hexi664/pm-review-board` 内置 skill 名为 `SPACE-review-board`, manifest 中以仓库别名 `pm-review-board` 作为引用 ID

### 6.5.2 设计阶段: frontend-design

- **触发位置**:`uses_skill: frontend-design` 同时挂在两个 stage 上
  - `stage5.ui_design` — 写 `04b_<项目名>_UI设计.md` 与 `prototype.html` 时, 把 frontend-design 作为设计哲学源头
  - `stage6.implementation#web` — 写 `源代码/<项目名>-web/` 实际源码时, 同样以 frontend-design 作为视觉指导思想
- **职责**: 提供"先定 token + 节奏 + 签名元素, 再写代码"两段式工作流, 拒绝 AI 默认三件套 (奶油底+棕红强调 / 纯黑底+荧光绿 / 报版三件套)
- **前置要求**: 调用 `$frontend-design` skill 读取其完整设计哲学 (已在本地 `$CODEX_HOME/skills/frontend-design` 安装)
- **约束落地 (见 `prompts/coding.md` 前端约束区)**:
  - 调色 4 个具名 hex, 排版 3 角色, 至少一个标志性元素, 至少一处可辩护的"出格选择"
  - 不允许把 frontend-design 当成"再加几行 CSS"

### 6.5.3 注入点对照表

| 阶段 | 注入 Skill | 触发 stage | 产物 |
|------|-----------|-----------|------|
| Phase 1 / 需求 | `pm-review-board` | `phase1.review` | `01_<项目名>_需求评审记录.md` |
| Phase 2 / Stage 5 | `frontend-design` | `stage5.ui_design` | `04b_<项目名>_UI设计.md` + `prototype.html` |
| Phase 2 / Stage 6 (web 子任务) | `frontend-design` | `stage6.implementation` | `源代码/<项目名>-web/` |


## 7. 强制 UI Artifact 规则 (v0.3.0 继承)

任何含有前端 UI 的项目都必须塞 UI design artifact:

- 进入 Stage 5 (UI Design) 时, 读取 prompt 强制条款, 生成至少 1 个 HTML 原型 + CSS 变量
- 不允许 `skip_when`
- token 紧张时, 压缩原型 (单页 + 状态/tab) 而非 skip

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




## 10. v0.5.3 变更日志 (本次修正)

### v0.5.3 — 恢复标题手写编号 (fix_docx_headings.py 退化症补丁)

**问题**: 用户在 taskmgr demo 上跑 v0.5.1 后反馈 "生成的详细设计文档并不符合模板, 标题的前面数字也没了". 排查发现 v0.5.1 走了两条互斥的修复路径 - 同时 "删手写 + 关模板自动", 导致 .docx 标题完全没编号.

**修复**:

- `templates/02_详细设计文档_九节骨架.md` 恢复 `## 一、文档说明` / `### 1.1 内容概要` 手写编号 (v0.5.0 时代被 v0.5.1 误删).
- `prompts/architecture.md` Step 1 + Step 1.5 重写:
  - Step 1 加 "v0.5.3 编号策略" 段, 明确要求文本里手写中文 / 阿拉伯编号.
  - Step 1.5 加入 "v0.5.1 退化症" + "v0.5.3 修复" 病史, 防止下次又走错路.
  - "不允许做的事" 加新禁令: v0.5.3 起不许再删手写编号.
- `SKILL.md` 搂5.2 顶部加 v0.5.3 修正说明 + 搂10 加本条 changelog.

**未自动修复的部分** (需要用户提供具体反馈才能修):

1. 用户提到 "生成的详细设计文档并不符合模板" - 这是另一个症状, 可能涉及: docx skill 没有用上 "详细设计模板.docx" 作为样式基线 / 封面丢了 / 字体配色错. **请提供 taskmgr 生成的 .docx 截图或上传文件**, 我才能具体定位.
2. 用户提到 "测试过程中也没有打开浏览器" - v0.5.2 已经加了 Stage 8 强制步骤, 但需要确认 (a) taskmgr 是不是 `has_frontend` 项目 (b) agent 走 Stage 8 时是否调了 control-in-app-browser. **请提供 taskmgr 工作空间 `06_*_验收报告.md` 或 `screenshots/08-*.png` 的内容**, 我能看到 Stage 8 是否执行.

---

## 16. v0.6.0 变更日志

### 新增

- **新增 pm-review-board 注入点 (需求阶段)**:
  - `skill-manifest.yaml` 注册 `pm-review-board` (仓库别名, 实际 skill 名 `SPACE-review-board`)
  - `workflow.yaml` 新增 `phase1.review` 阶段, 在 `phase1.spec` 之后 / Phase 2 之前
  - `prompts/requirement.md` 新增 step 6: PRD 6 角色自检评审
  - `SKILL.md` 新增 6.5.1 章节描述触发位置 / 输入 / 输出 / 门禁
- **新增 frontend-design 注入点 (设计阶段)**:
  - `skill-manject.yaml` 注册 `frontend-design` (本地已装, source=bundled)
  - `workflow.yaml` 把 `frontend-design` 挂在 `stage5.ui_design` 与 `stage6.implementation#web`
  - `prompts/coding.md` 前端约束区补设计哲学落地 5 条 + 别再忘记补一条
  - `SKILL.md` 新增 6.5.2 章节描述两段式工作流 (token + 节奏 + 签名元素 → 写代码)
- **SKILL.md 新增 6.5.3 注入点对照表**

### 反馈来源

用户希望把多角色 PRD 评审前置到需求阶段末尾, 避免 Phase 2 写代码后才发现需求漏洞; 同时把前端视觉设计从"通用 AI 默认风格"换成有原则的 `frontend-design`.


## 15. v0.5.5 变更日志

### v0.5.5 — fix_docx_headings.py 默认不剥手写编号 (二级标题回归 fix)

**症状**: 用户反馈 H1 有编号 "一、", 但 H2 / H3 没编号.

**根因**: `fix_docx_headings.py` 默认调用 `strip_leading_numbers()`, 把 v0.5.3+ 故意写的 "1.1 / 1.1.1" 前缀也剥了. 而模板自动编号又已经被 numId=0 关掉, H2/H3 渲染后就没前缀了. H1 显示 "一、" 不受影响是因为 `^\d+` 正则不匹配中文.

**改动**:

- `scripts/fix_docx_headings.py`: 新增 `--strip-leading-numbers` flag (默认 **False**), `fix_one()` 加同名参数, 默认传 False, 主循环不再剥手写编号.
- `templates/02_详细设计文档_九节骨架.md`: 顶部 "v0.5.3 编号策略" 注释升到 "v0.5.5 编号策略", 明确 "默认不剥".
- `SKILL.md` `version: 0.5.4` → `0.5.5`. `workflow.yaml` `version: v0.5.4` → `v0.5.5`.

**反馈来源**: 跑 DEMO 验收后用户原话 "详细设计的一级标题有了 但是二级标题还是没有. 更新skill" → 立即根据实际 H2 数据反向追源, 发现 fix_docx_headings.py 误剥.

---

## 14. v0.5.4 变更日志

### v0.5.4 — iab API 现实落库 (本次升级)

**目标**: 把 Codex in-app browser 面板的真实可用 API 写进 skill, 避免 agent 再去试 `tab.screenshot` / `evaluate` / `domSnapshot` 这些"听起来能用但 hang 或 undefined"的方法.

**实测结论**:

| API | 状态 |
|-----|------|
| `tab.dom_cua.get_visible_dom()` | ✅ 返回带 node_id 的 DOM 字符串 |
| `tab.dom_cua.click({node_id})` | ✅ 节点驱动的 click |
| `tab.dom_cua.type({text})`     | ✅ 焦点元素 type |
| `tab.cua.click(x,y)`           | ✅ 坐标驱动的 click |
| `tab.cua.type({text})`         | ✅ 焦点 type |
| `tab.screenshot({path})`       | ❌ hang (Statsig analytics) |
| `tab.content.export()`         | ❌ iab 不支持 |
| `tab.playwright.evaluate(...)` | ❌ 返回 undefined |
| `tab.playwright.domSnapshot()` | ❌ 抛错 |

**改动**:

- `prompts/review.md` 阶段 2 整段重写, 用 dom_cua + node_id, 移除所有 `tab.locator(...)` /`tab.screenshot` /`tab.evaluate` 字眼.
- `workflow.yaml` Stage 8 `browser.open_in_app_panel` 的 `forbidden_alternatives` 加 4 条坏 API 禁用.
- `SKILL.md` 搂2 加 4 条 v0.5.4 新禁令, 搂14 加本 changelog.
- 新增 `docs/iab-stage8-notes.md` 把踩坑记录独立成文件, 方便 agent 调 `agent.documentation.get('iab-stage8-notes')`.

**反馈来源**: 用户跑 DEMO 验收阶段反馈 `"现在打开了浏览器。把这个思路强制写入 skill 里 其它步骤可以停了先"` → 明确要把"实测可用的 API = dom_cua + node_id, 不要 tab.screenshot / evaluate" 强写到 skill.

---

## 13. v0.5.3 变更日志
## 11. v0.5.2 变更日志## 10. v0.5.2 变更日志

### v0.5.2 — Stage 8 强制打开右侧 in-app browser 面板 (本次升级)

**目标**: 用户跑 demo 时能实时在 Codex 对话框**右边**看到测试过程. 之前是 agent 自觉开, 现固化为 Stage 8 必选步骤.

**改动**:

- `workflow.yaml` Stage 8 新增 `browser.open_in_app_panel` 步骤, `required: true`, `on_failure: stop_workflow`.
- Stage 8 含 4 个子步骤: `open_in_app_panel` (强制) → `interact` → `compose_report` → `optional_record` (ffmpeg 录屏, 默认关).
- Stage 8 `forbidden_alternatives`: 不允许 `chromium.launch({ headless: true })` 纯 headless 跑完后只交 screenshots/.
- `prompts/review.md` 阶段 2 整段重写, 把 in-app browser 调用规约写成具体代码 (browser-client 初始化 + `tab.goto` + `tab.locator.click`).
- `SKILL.md` 搂2 加新约束, 搂6 Stage 8 表格加 v0.5.2 标记, 搂10 顶部加本条 changelog.

**反馈来源**: 用户上一轮"之前 codex 测试时有打开过的 就是对话框的右边" → 显式把"打开右侧 in-app browser 面板"做成 skill 强约束.

**未做 (可选)**: ffmpeg 自动录屏默认关, 由用户 opt-in 启用 (录屏很占 CPU 且 ffmpeg 不一定装). 后续如需要, 加 `optional_record` 步骤 + `--user-opt-in-record` 启动参数.

## 12. v0.5.1 变更日志

### v0.5.1 (上一版, 标题去重 + 业务模块强约束)

**新增 / 强化**:

- 新增 `scripts/fix_docx_headings.py` (~6.7KB, 仅依赖 python-docx): 打开 .docx 后处理, 把 Heading 1/2/3 段落的 pPr numId 强制设为 0 (禁用 Word 自动编号), 同时防御性清理文本里残留的 "1. " / "1.1 " / "1\t" 前缀, in-place 保存.
- `prompts/architecture.md` Step 1.5 从"软建议禁用自动编号"改成"**强制**调 scripts/fix_docx_headings.py", 加反例清单与禁用项.
- `templates/02_详细设计文档_九节骨架.md` 去掉 "## 一. 概述" 之类的"手写 + 自动"双重编号标题, 改为 "## 文档说明" (纯文字, 由 Word 自动渲染编号).
- `templates/03_架构设计.md` 全文重写, 加入"业务模块维度"骨架, 末尾附"反例清单"明确禁止 SpringBoot 技术分层与按 controller/service/repository 罗列.
- `prompts/architecture.md` Step 2 业务模块划分加"反例清单" (❌ 接入层/应用层/服务层/数据层/基础设施层 / ❌ controller/service/dao), 强制业务模块必须包含"问题描述"列.
- `prompts/architecture.md` Step 2.0 调用示例从 5 层技术分层改为 5 个业务模块示例.
- `scripts/render_arch.py` 默认 fallback 由"接入层/应用层/服务层/数据层/基础设施"改为业务模块示例, 并增加"占位提示"提醒 agent 用真实业务模块重画.
- `SKILL.md` 搂5.2 重新组织: 改为"强制调 scripts/fix_docx_headings.py"为标题级, 把禁用项与验收标准文档化.
- `SKILL.md` 搂5.3 在原架构图自动生成文档基础上, 顶部加"业务模块维度强制 + 反例清单".
- `SKILL.md` 搂2"不做什么"加 3 条新约束: 不交付未修复 Heading 的 .docx / 不手写编号 / 架构图不按技术分层.
- `workflow.yaml` Stage 2 步骤新增 fix_docx_headings 节点.

### 反馈来源
用户在 v0.3.0 时反馈 "模块划分怎么是 SpringBoot 的结构分层? 不应该是实际的业务模块吗", 落到 v0.5.0 时仍未解决; 用户在 v0.4.0 时反馈 "根据 word 模板生成的新文件的 head 节点前面多了数字 (1 1 文档说明 / 1.1 1.1 内容概要)", 落到 v0.5.0 时仍未稳定修复. v0.5.1 把这两条做成强约束 (脚本兜底 + 反例清单), 不再依赖 agent 自己按 prompt 行事.

### v0.5.0 (上一版)
- 新增架构图自动生成能力
  - 新增 `scripts/render_arch.py` (matplotlib 后端, 中文 fallback, 支持 .md/.json/CLI 三种输入)
  - `SKILL.md` 搂5.3 文档化架构图生成规则
  - `workflow.yaml` Stage 3 产出新增 `03_<项目名>_架构图.png`
  - `prompts/architecture.md` Step 0 新增"先调用 render_arch.py 再写 markdown"

### v0.4.2: 新增 WHERE_TEMPLATE.md 解释本地 skill 找模板的 4 级优先级
  - SKILL.md / coding.md 去掉 CEC 引用
  - examples 真实项目名 -> 通用示例
  - README.md / docs/usage.md 触发示例同步替换
  - 模板文件 (.docx) 仍在 .gitignore, 用户私有资产

### v0.4.0: 修复模板自动编号双重叠加 (软约束, v0.5.1 升级为强制)
  - `prompts/architecture.md` 新增 Step 1.5: 建议 `disable_auto_number(p)` 把 numId=0
  - `SKILL.md` 搂5.2 文档化症状/根因/修复
  - `SKILL.md` 搂5.1 文档化首次安装后模板准备流程

### v0.3.0: 修复详细设计模板查找路径 (4 级优先级 + `--template=`)
### v0.2.0: NN_<项目名>_<文档名> 命名约定 + 单工作空间目录 + 中文文件名
### v0.1.0: 初始 scaffold