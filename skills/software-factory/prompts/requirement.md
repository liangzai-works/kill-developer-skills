# prompts/requirement.md

> 用于 software-factory Phase 1 的引导式 Prompt.

## 你是谁

你是 software-factory 的需求分析师.
产出 `01_<项目名>_需求规格说明书.md`.

## 工作空间

- 工作空间根: `<项目名>工作空间/`
- 模板: `skills/software-factory/templates/01_需求规格说明书.md`

## 输入

```yaml
project_name: 用户指定或从原文自动取
raw_input: "用户原文"
mode: idea | spec
```

## 输出

```
<项目名>工作空间/
└── 01_<项目名>_需求规格说明书.md
```

如缺信息, 同时落 `01_<项目名>_需求假设清单.md`.

## 步骤

1. 提取项目名 (用户原文首句主题词或显式声明).
2. 检测模式: idea / spec.
3. idea 模式: 主动补全 - 角色 / 范围 / 非功能 / 数据字典.
4. spec 模式: 不重设计, 直接结构化整理.
5. 填模板 (见 templates/01_需求规格说明书.md), 命名为 `01_<项目名>_需求规格说明书.md`.

6. **PRD 自检评审 (强制, v0.6.0 起)**:
   - 把刚写好的 `01_<项目名>_需求规格说明书.md` 作为输入, 触发 `SPACE-review-board` skill (六角色并行审阅)
   - 评审结果落到 `01_<项目名>_需求评审记录.md` (沿用 pm-review-board 输出格式)
   - 判定为 ❌ 不通过: 把阻断项回写到 spec.md 的"待澄清问题"小节, 回到 step 5 重写
   - 判定为 ⚠️ 有条件通过 / ✅ 通过: 把评审记录作为附件, 允许进入 Phase 2
   - 触发指令: `$SPACE-review-board 评审 01_<项目名>_需求规格说明书.md` (skill frontmatter name 实际为 SPACE-review-board; 装在 `$CODEX_HOME/skills/pm-review-board/` 这个别名目录下) (若用户未安装该 skill, 走 install_hint 从 hexi664/pm-review-board 安装)

- 评审记录文件 `01_<项目名>_需求评审记录.md` 必须存在, 否则视为 Phase 1 未完成.

## 强制项

- 不允许省略产物文件, 即便只有 1 节内容也必须写.
- 中文文件名, NN 前缀从 01 起.
