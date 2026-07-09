# Spec-Mode 示例: 通用业务管理系统

> Spec 模式的输入样例. 展示用户已经给出详细需求/技术栈时, skill 应如何处理.
> 这是**虚构**的样例, 用于演示 skill 工作流, 不是真实项目.

## 用户原文 (结构化)

```
项目: 业务管理系统 (示例)
技术栈:
  - 后端: JDK 21 + Spring Boot 3.x + Spring Data JPA
  - 数据库: MySQL (生产) / SQLite (开发 / 测试)
  - 前端: Bootstrap 5 + ECharts (CDN) + Thymeleaf SSR
  - 不做前后端分离; 不接入鉴权

功能范围 (仅 V1):
  1. 首页 (工作台): 关键指标概览, 近 7 日趋势
  2. 节点管理:
     - 列表 (分页, 筛选, 按标签)
     - 新增 / 修改 / 删除
     - 启停 / 批量启停
     - 标签管理

架构约束:
  - 三层架构: PageController + ApiController + Service + Repository
  - 统一 ApiResult<T>
  - SeedDataRunner 注入 >= 50 条用于演示
```

## 应有的工作流反应

1. Phase 1.detect_mode 命中 Spec 模式.
2. **不重新设计**; 原样落 `raw-input.md`, 生成 `gap-list.md` 列缺什么.
3. 用户在跑前至少补: 默认账号, 部署端口, 是否需要导出.
4. 跳过 Architecture 重设计 (仅做接口级落地), 直接进 Stage 5.