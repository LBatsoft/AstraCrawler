"""
示例脚本：演示如何使用调度器提交爬取任务
"""
import time
from astra_scheduler.dispatcher import schedule_task, get_task_status, get_task_result


def main():
    """主函数"""
    # 提交一个高优先级任务
    print("提交爬取任务...")
    task = schedule_task(
        url="https://example.com",
        priority="high"
    )
    
    print(f"任务已提交，ID: {task.id}")
    
    # 轮询任务状态
    print("等待任务完成...")
    while True:
        status = get_task_status(task.id)
        print(f"任务状态: {status['status']}")
        
        if status["status"] in ["SUCCESS", "FAILURE"]:
            break
        
        time.sleep(2)
    
    # 获取结果
    if status["status"] == "SUCCESS":
        result = get_task_result(task.id)
        print(f"\n爬取成功！")
        print(f"URL: {result.get('url')}")
        print(f"标题: {result.get('title')}")
        print(f"HTML 长度: {len(result.get('html', ''))} 字符")
    else:
        print(f"\n任务失败: {status.get('traceback')}")


if __name__ == "__main__":
    main()

