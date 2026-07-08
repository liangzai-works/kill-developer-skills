# workspace/

> `software-factory` 运行的 Artifact 落地目录。
> 每个子目录对应一个 Stage 的产物，**严格按 Stage 顺序写**。

```
workspace/
├── requirements/   ← Phase 1 产物：原始输入、需求分析、PRD
├── design/         ← Stage 2-4 产物：原型、UI 规范、架构
├── development/    ← Stage 5-6 产物：源码、运行日志
├── testing/        ← Stage 7-8 产物：测试报告、评审报告
└── delivery/       ← 最终交付：总结报告、截图
```

## 目录规则

| 目录 | 是否必须 | 何时清理 | 何时锁定 |
|------|----------|----------|----------|
| requirements/ | ✅ | 重跑 Phase 1 时清空 | 进入 Phase 2 后只读 |
| design/ | ✅ | 重跑 Stage 1 时清空 | Stage 5 启动后只读 |
| development/ | ✅ | -- | 跑完 Stage 6 即归档 |
| testing/ | ✅ | -- | 交付前最后一次写入 |
| delivery/ | ✅ | -- | 永远 append-only |

## 不变约束

- 禁止跨 Stage 直传上下文，**只允许通过本目录文件传递**。
- 已归档的目录视为只读；要改就重跑对应 Stage。
- 不在本目录放临时调试文件；临时文件放 `<project>/tmp/`。
