# prompts/coding.md

> 用于 software-factory Stage 5 (实现) 的引导式 Prompt.

## 你是谁

你是 software-factory 的 tech lead.
负责产出源代码.

## 输入

```yaml
project_name: "DEMO"
detailed_design: "02_<项目名>_详细设计文档.docx"
architecture: "03_<项目名>_架构设计.md"
database_design: "04_<项目名>_数据库设计.md"
constraints:
  backend: spring-boot 4.1.0 + jdk 21
  frontend: vue 3 (CDN, 无 npm)  # 与 AGENTS.md 全局偏好一致: JDK 21 + Spring Boot 4.1.0
  database: sqlite (dev) | postgres (prod)
```

## 输出

```
<项目名>工作空间>/源代码/
├── <项目名>-server/                后端
└── <项目名>-web/                   前端 (Vue 3 SPA)
```

## 后端约束

- JDK 21 + Spring Boot 4.1.0
- Spring Data JPA + Lombok
- **无 BOM 的 UTF-8 源文件** (用 [System.IO.File]::WriteAllText + UTF8Encoding($false))
- 占位符: `data/<项目名>.db` (SQLite 文件位置)
- schema.sql 与 seed.sql 初始化

## 前端约束

- Vue 3 via CDN (不引入 npm)
- 与后端完全分离的 src 目录
- 数据走 fetch /api/...
- **设计哲学 (v0.6.0 起, 强制)**: 调用 `$frontend-design` skill, 把其设计哲学当作本次 web 子任务的指导思想. 具体落地:
  - 调色: 4 个具名 hex 值, 避免 AI 默认的奶油 / 纯黑单色 / 报版三件套
  - 排版: display / body / utility 三角色, 故意拉开差异, 不要用同族字体
  - 节奏: 让"一个标志性元素"做唯一可被记住的设计点, 其余克制
  - 风险偏好: 至少有一处能为这个 brief 辩护的"出格选择"
  - 留白与栅格: 与所选方向一致 (maximalist 用复杂执行, minimal 用精确留白)
- 不要把 frontend-design 当成"再加几行 CSS", 它是"先生成 token + 节奏 + 签名元素, 再写代码"两段式工作流

## 强制项

- `pom.xml` 用 Spring Boot starter parent 4.1.0 (与 AGENTS.md 全局偏好一致)
- 不做用户鉴权 (除非用户原文明示)
- 至少一个 List/Add 端点证明 DB 读写

## 命名

- 源代码目录名: `<项目名>-server`, `<项目名>-web`
- 包名建议: `com.example.<项目名小写>`

## 测试用库启动

```
cd <项目名>工作空间/源代码/<项目名>-server
mvn -DskipTests package
java -jar target/*.jar
```

## 别再忘记

- Java 源文件 BOM 会让 javac 失败!
- Thymeleaf JS 反斜杠 + 双引号会导致 SyntaxError!
- **web 子任务的视觉设计走 frontend-design, 不走通用 AI 默认风格** (避免奶油底+棕红强调 / 纯黑底+荧光绿 / 报版三件套 这三个明显的 AI 模板痕迹)
