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
  backend: spring-boot 3.x + jdk 21
  frontend: vue 3 (CDN, 无 npm)
  database: sqlite (dev) | postgres (prod)
```

## 输出

```
<项目名>工作空间>/源代码/
├── <项目名>-server/                后端
└── <项目名>-web/                   前端 (Vue 3 SPA)
```

## 后端约束

- JDK 21 + Spring Boot 3.x
- Spring Data JPA + Lombok
- **无 BOM 的 UTF-8 源文件** (用 [System.IO.File]::WriteAllText + UTF8Encoding($false))
- 占位符: `data/<项目名>.db` (SQLite 文件位置)
- schema.sql 与 seed.sql 初始化

## 前端约束

- Vue 3 via CDN (不引入 npm)
- 与后端完全分离的 src 目录
- 数据走 fetch /api/...

## 强制项

- `pom.xml` 用 Spring Boot starter parent 3.3.x
- 不做用户鉴权 (除非用户原文明示)
- 至少一个 List/Add 端点证明 DB 读写

## 命名

- 源代码目录名: `<项目名>-server`, `<项目名>-web`
- 包名建议: `com.cec.<项目名小写>`

## 测试用库启动

```
cd <项目名>工作空间/源代码/<项目名>-server
mvn -DskipTests package
java -jar target/*.jar
```

## 别再忘记

- Java 源文件 BOM 会让 javac 失败!
- Thymeleaf JS 反斜杠 + 双引号会导致 SyntaxError!
