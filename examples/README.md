# AstraCrawler 示例脚本

本目录包含 AstraCrawler 的各种使用示例。

## 示例列表

### 1. demo_task.py
基础任务提交示例，演示如何使用调度器提交爬取任务。

```bash
python examples/demo_task.py
```

### 2. demo_with_hooks.py
带钩子脚本的爬取示例，演示如何注入 JavaScript 钩子脚本。

```bash
python examples/demo_with_hooks.py
```

### 3. demo_data_processing.py
数据处理示例，演示如何使用数据处理管道提取和清洗数据。

```bash
python examples/demo_data_processing.py
```

### 4. demo_jsrpc.py
JsRpc 集成示例，演示如何使用 JsRpc 进行前端加密破解。

**前置要求**:
- JsRpc 服务端运行在 `ws://localhost:12080`
- 可以从 https://github.com/jxhczhl/JsRpc 下载服务端

```bash
# 1. 启动 JsRpc 服务端
# 2. 运行示例
python examples/demo_jsrpc.py
```

## 运行所有示例

```bash
# 确保 Redis 和 JsRpc 服务端正在运行
python examples/demo_task.py
python examples/demo_with_hooks.py
python examples/demo_data_processing.py
python examples/demo_jsrpc.py
```

## 注意事项

1. 运行示例前确保相关服务已启动（Redis、JsRpc 等）
2. 某些示例需要网络连接访问目标网站
3. JsRpc 示例需要单独启动 JsRpc 服务端

