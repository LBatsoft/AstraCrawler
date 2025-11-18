# AstraCrawler 示例脚本

本目录包含 AstraCrawler 的使用示例。

## 示例列表

### demo_get_encrypted_params.py

获取加密参数的实际案例，演示如何使用 JsRpc 在实际场景中获取加密参数。

**功能**:
- 获取签名参数
- 模拟真实网站的加密破解流程
- 批量获取多个页面的加密参数
- 构建完整的 API 请求头

**前置要求**:
- JsRpc 服务端运行在 `ws://localhost:12080`
- 可以使用 `tests/jsrpc_mock_server.py` 启动模拟服务端

**运行方式**:

```bash
# 方式 1: 手动启动服务端（推荐用于测试）
# 终端 1: 启动 JsRpc 服务端
python tests/jsrpc_mock_server.py

# 终端 2: 运行示例
python examples/demo_get_encrypted_params.py

# 方式 2: 使用真实 JsRpc 服务端
# 从 https://github.com/jxhczhl/JsRpc 下载并运行服务端
# 然后运行示例
python examples/demo_get_encrypted_params.py
```

**示例输出**:
- Token 获取过程
- 签名参数生成过程
- 完整请求头构建
- 批量请求处理

## 注意事项

1. 运行示例前确保 JsRpc 服务端正在运行
2. 示例中使用无头浏览器模式（headless=True）
3. 示例中的加密函数是模拟的，实际场景中需要找到真实网站中的函数

## 参考文档

- [JsRpc 集成指南](../docs/JSRPC_GUIDE.md)
- [获取加密参数指南](../docs/ENCRYPT_PARAMS_GUIDE.md)
- [真实场景使用指南](../docs/REAL_WORLD_USAGE.md)
