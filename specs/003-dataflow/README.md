---
title: 数据处理 (Dataflow)
status: complete
priority: medium
assignee: morein
created: 2025-01-27T10:00:00Z
tags:
  - pipeline
  - storage
  - jsonl
---

# 数据处理 (Dataflow)

## 1. 数据管道

### 1.1 处理流程
- **场景**: 接收到 Worker 返回的 Raw Data (HTML + Hook Data)
- **行为**:
  1. HTML 解析提取 (Title, Text, Links)。
  2. 数据清洗 (去除空白，规范化)。
  3. 合并 Hook 数据。
  4. 添加处理时间戳。
  5. 持久化存储。

### 1.2 持久化存储
- **场景**: 处理完成
- **行为**: 将结果追加写入到 `data/output/{DATE}.jsonl` 文件。
- **验证**:
  - 文件存在。
  - 文件内容为有效的 JSON Lines 格式。
  - 数据字段完整。
