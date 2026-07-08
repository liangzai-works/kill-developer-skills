# INSTALL.md

把 `software-factory` Meta Skill 注册到 Codex。

## 方式 A — 个人市场（推荐）

```powershell
$dest = "$env:CODEX_HOME\marketplaces\personal\.codex-plugin"
if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Force -Path $dest | Out-Null }
Copy-Item -Recurse -Force `
  "C:\work\skills-workspace\kill-developer-skills\skills\software-factory" `
  "$dest\software-factory"
```

## 方式 B — 全局 skills 目录

```powershell
$dest = "$env:CODEX_HOME\skills\software-factory"
Copy-Item -Recurse -Force `
  "C:\work\skills-workspace\kill-developer-skills\skills\software-factory" `
  $dest
```

## 验证

重启 Codex 或刷新 Skill 列表，触发：

```
$software-factory --status
```

应输出：

```
workflow: software-factory
phase: idle
skills: manifest loaded (12 required, 0 missing)
```

## 卸载

直接删 `$CODEX_HOME/skills/software-factory/`（或 `$dest\software-factory`）。
