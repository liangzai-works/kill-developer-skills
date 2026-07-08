# workspace/development/

> Stage 5-6 落地目录。

## 约定结构

```
development/
├── source-code/          ← Stage 5：完整可构建工程
│   ├── pom.xml
│   ├── src/main/java/...
│   ├── src/main/resources/...
│   └── README.md
├── runtime.log           ← Stage 6：启动日志
└── health-check.json     ← Stage 6：健康检查响应
```

## Source-code 子约定

- 与主项目同名 / 同结构。
- 不允许把代码再拆成多个 micro repo（本 Meta Skill 不做 mono-repo 编排）。
- `README.md` 写清：
  - 启动命令
  - 默认端口
  - 默认账号 / 路径

## 完成态

进入 Stage 7 前：

- [ ] `mvn -DskipTests package` 成功（或对应构建命令）
- [ ] 启动日志中无 `ERROR` 级条目
- [ ] `/actuator/health` 返回 `UP`
- [ ] 健康检查 JSON 已落 `health-check.json`
