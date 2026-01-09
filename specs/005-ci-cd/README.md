---
title: CI/CD 流水线
status: complete
priority: medium
assignee: morein
created: 2025-01-27T11:00:00Z
tags:
  - devops
  - github-actions
  - testing
---

# CI/CD 流水线

## 1. 自动化测试

### 1.1 单元测试
- **场景**: 每次 Push 或 Pull Request 到 main/master 分支
- **行为**:
  - 设置 Python 3.9/3.10/3.11 环境。
  - 安装依赖 (`requirements.txt` + `test` 依赖)。
  - 运行 `pytest`。
- **验证**:
  - 所有非集成测试通过。
  - 无回归错误。

### 1.2 代码质量检查 (Linting)
- **场景**: 每次 Push 或 PR
- **行为**: 运行 `flake8` 或 `ruff`。
- **验证**: 代码风格符合规范，无语法错误。

## 2. 构建验证

### 2.1 Docker 构建
- **场景**: 每次 Push 到 main/master
- **行为**: 尝试构建 Docker 镜像。
- **验证**: `docker build` 成功，确保 Dockerfile 有效性。
