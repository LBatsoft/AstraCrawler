"""
拟人化行为模块

模拟真实用户操作，如非线性鼠标移动、随机滚动等，用于欺骗基于行为分析的反爬系统。
"""
import random
import asyncio
import math
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def bezier_curve(
    start: Tuple[int, int], 
    end: Tuple[int, int], 
    control_point: Tuple[int, int], 
    steps: int
) -> List[Tuple[int, int]]:
    """生成二阶贝塞尔曲线路径"""
    path = []
    for i in range(steps):
        t = i / steps
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control_point[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control_point[1] + t**2 * end[1]
        path.append((int(x), int(y)))
    return path

async def simulate_mouse_movement(page):
    """
    模拟拟人化鼠标移动
    随机移动到页面中心区域，轨迹平滑且带随机扰动
    """
    try:
        # 获取视口大小
        viewport = page.viewport_size
        if not viewport:
            return
            
        width, height = viewport["width"], viewport["height"]
        
        # 起点 (假设当前鼠标位置或左上角)
        start_x, start_y = random.randint(0, 100), random.randint(0, 100)
        
        # 终点 (随机选择视口中心区域的一个点)
        end_x = random.randint(int(width * 0.2), int(width * 0.8))
        end_y = random.randint(int(height * 0.2), int(height * 0.8))
        
        # 控制点 (用于生成曲线)
        control_x = random.randint(0, width)
        control_y = random.randint(0, height)
        
        # 生成路径
        steps = random.randint(20, 50) # 步数越多越慢
        path = bezier_curve((start_x, start_y), (end_x, end_y), (control_x, control_y), steps)
        
        # 执行移动
        for x, y in path:
            await page.mouse.move(x, y)
            # 随机极短停顿，模拟微颤
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.001, 0.01))
            
        logger.debug(f"已执行拟人化鼠标移动: ({start_x},{start_y}) -> ({end_x},{end_y})")
        
    except Exception as e:
        logger.warning(f"拟人化鼠标移动失败: {str(e)}")

async def simulate_scrolling(page):
    """
    模拟拟人化滚动
    随机向下滚动一段距离，模拟阅读
    """
    try:
        # 随机滚动次数
        scrolls = random.randint(1, 3)
        
        for _ in range(scrolls):
            # 随机滚动距离 (100px - 500px)
            distance = random.randint(100, 500)
            
            # 使用 evaluate 平滑滚动
            await page.evaluate(f"""
                window.scrollBy({{
                    top: {distance},
                    behavior: 'smooth'
                }});
            """)
            
            # 随机停顿 (模拟阅读)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
        logger.debug(f"已执行拟人化滚动: {scrolls} 次")
        
    except Exception as e:
        logger.warning(f"拟人化滚动失败: {str(e)}")

async def human_like_interaction(page):
    """执行一套完整的拟人化交互"""
    await simulate_mouse_movement(page)
    await asyncio.sleep(random.uniform(0.2, 0.8))
    await simulate_scrolling(page)

