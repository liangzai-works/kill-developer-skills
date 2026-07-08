# workspace/design/

> Stage 2-4 落地目录。

## 约定文件

| 文件 | 必填 | 来源 | 用途 |
|------|------|------|------|
| `prototype/` | ⬜ | Stage 2 | 原型 HTML / Figma 链接 |
| `ui-spec.md` | ⬜ | Stage 2 | UI 规范（页面 / 交互） |
| `design-system.md` | ⬜ | Stage 3 | 设计系统 / 组件库定义 |
| `component-spec.md` | ⬜ | Stage 3 | 组件规范 |
| `architecture.md` | ✅ | Stage 4 | 总体架构 |
| `api-spec.md` | ✅ | Stage 4 | 接口规范 |
| `db-schema.md` | ✅ | Stage 4 | 数据库 Schema |

> ⬜ 标记的文件，当项目类型为 `cli` 或 `backend-only` 时可缺失。

## 完成态

进入 Stage 5 前必须满足：

- [ ] architecture.md 9 节齐备
- [ ] api-spec.md 中每个功能点至少有 1 个接口
- [ ] db-schema.md 已有可执行的建表 SQL
