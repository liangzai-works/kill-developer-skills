# Design — {{project_name}}

> 由 `software-factory` 在 Stage 4 (Architecture Design) 产出。
> 输入：`requirements/PRD.md`、可选 `design/ui-spec.md`。
> 产物三件套：`architecture.md`（本文）/ `api-spec.md` / `db-schema.md`。

## 0. 元信息

| 字段 | 值 |
|------|----|
| 项目名称 | |
| 架构版本 | v0.1.0 |
| 编制日期 | |
| 依据 PRD 版本 | |

## 1. 架构总览

> 用一张 / 多张图说明：
> - 客户端（SSR / SPA）
> - 应用层（Controller / Service）
> - 持久层（JPA / Repository）
> - 外部依赖（DB / 缓存 / MQ）

## 2. 技术栈

| 层 | 选型 | 版本 | 理由 |
|----|------|------|------|
| 后端语言 | Java | 21 | |
| 框架 | Spring Boot | 3.3.x | |
| ORM | Spring Data JPA | | |
| 模板引擎 | Thymeleaf | | 仅 SSR |
| 数据库 | SQLite (开发) / MySQL (生产) | | |
| 前端 | Bootstrap 5 + ECharts (CDN) | | 简化栈 |

## 3. 模块划分

| 模块 | 职责 | 主要入口 |
|------|------|----------|
| | | |

## 4. 类设计（核心）

> 列出 Service / Repository / Controller 关键类与依赖。

## 5. 时序图

> 关键场景（如"列表查询"、"新增节点"、"状态翻转"）的时序。

## 6. 数据库设计（初版）

> 完整 SQL Schema 见 `db-schema.md`。

| 表 | 关键字段 | 索引 | 备注 |
|----|----------|------|------|
| | | | |

## 7. API 设计（初版）

> 完整接口见 `api-spec.md`。

| Method | Path | 用途 | 鉴权 |
|--------|------|------|------|
| | | | |

## 8. 横切关注点

- 异常处理：统一 `ApiResult` 包装
- 日志：MDC + JSON
- 配置：`application.yml` + 环境变量覆盖
- 安全：本版本暂不接入登录；预留 `X-User-Id` 透传字段

## 9. 部署与运行

- 构建：`mvn -DskipTests package`
- 启动：`java -jar target/*.jar`
- 健康检查：`GET /actuator/health` 或自定义 `/api/ping`
