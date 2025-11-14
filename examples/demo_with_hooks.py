"""
示例脚本：演示如何使用钩子脚本进行爬取
"""
import time
from astra_scheduler.dispatcher import schedule_task, get_task_status, get_task_result
from astra_reverse_core.utils import get_default_hooks


def main():
    """主函数"""
    # 获取默认钩子脚本
    hook_scripts = get_default_hooks()
    print(f"加载了 {len(hook_scripts)} 个钩子脚本")
    
    # 提交带钩子的爬取任务
    print("提交带钩子的爬取任务...")
    task = schedule_task(
        url="https://example.com",
        priority="high",
        options={
            "headless": True,
            "timeout": 30000
        },
        hook_scripts=hook_scripts
    )
    
    print(f"任务已提交，ID: {task.id}")
    
    # 等待任务完成
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
        
        # 注意：钩子拦截的数据需要在页面中通过 JavaScript 获取
        # 这里只是演示任务提交流程
    else:
        print(f"\n任务失败: {status.get('traceback')}")


if __name__ == "__main__":
    main()

