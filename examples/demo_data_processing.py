"""
示例脚本：演示数据处理管道
"""
from astra_dataflow.pipeline import DataPipeline


def main():
    """主函数"""
    # 示例 HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>示例页面</title>
        <meta name="description" content="这是一个示例页面">
    </head>
    <body>
        <h1>欢迎使用 AstraCrawler</h1>
        <p>这是一个用于演示数据处理功能的示例页面。</p>
        <a href="https://example.com">示例链接</a>
        <img src="image.jpg" alt="示例图片">
        <table>
            <tr><th>列1</th><th>列2</th></tr>
            <tr><td>数据1</td><td>数据2</td></tr>
        </table>
    </body>
    </html>
    """
    
    # 创建处理管道
    pipeline = DataPipeline(enable_cleaning=True)
    
    # 处理数据
    result = pipeline.process(html_content, url="https://example.com")
    
    # 输出结果
    print("处理结果:")
    print(f"标题: {result.get('title')}")
    print(f"文本内容: {result.get('text')[:100]}...")
    print(f"Meta 信息: {result.get('meta')}")
    print(f"链接数量: {len(result.get('links', []))}")
    print(f"图片数量: {len(result.get('images', []))}")
    print(f"表格数量: {len(result.get('tables', []))}")


if __name__ == "__main__":
    main()

