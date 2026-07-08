# docs/extension.md

> 如何扩展 `kill-developer-skills` 到 Java / Python / Frontend / AIOps 等垂直工作流。

## 1. 扩展点

`software-factory` 的核心是 `workflow.yaml` + `skill-manifest.yaml`。  
要新增垂直工作流，**只需新增一个 `workflows:` 项**，不动主工作流。

## 2. Java Workflow 示例

```yaml
# skill-manifest.yaml
workflows:
  - id: java-workflow
    required-skills:
      - id: coding-java-spring
      - id: jpa-spec
      - id: sql-design
      - id: testing-junit
```

然后：

- 在 `skills/java-workflow/` 增加 `SKILL.md` 与 `workflow.yaml`。
- 在 `prompts/` 增加 `coding-java.md`。
- 在 `templates/` 增加 `ProjectLayout.md`（约定 Spring Boot 工程布局）。

主 Skill 在 Phase 0 扫描到 `workflows:` 字段后会自动注册。

## 3. 自定义校验

可以在 `skill-manifest.yaml` 里加一段 `custom_healthcheck`：

```yaml
custom_healthcheck:
  java-workflow:
    - shell: "mvn -version"
      must_contain: "21"
    - shell: "javac -version"
      must_contain: "21"
```

## 4. 版本兼容

- `manifest_version: v1` 当前稳定。
- 任何 v2 字段都会保留 v1 兼容至少 1 个 minor version。
- 想引入新字段：在 `skill-manifest.yaml` 顶部加 `extends:` 显式锁定 v1 schema。
