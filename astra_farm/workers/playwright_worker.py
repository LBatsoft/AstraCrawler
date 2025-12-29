"""
Playwright Worker 模块

使用 Playwright 执行网页爬取任务
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from celery.exceptions import Retry
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
# 尝试导入 playwright_stealth
try:
    from playwright_stealth import stealth_async
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False

from ..config import worker_config

# 配置日志
logger = logging.getLogger(__name__)

# 全局变量，用于持久化浏览器实例
_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None

# 创建 Celery 应用实例（与调度中心使用相同的配置）
celery_app = Celery(
    "astra_farm",
    broker=worker_config.CELERY_BROKER_URL,
    backend=worker_config.CELERY_RESULT_BACKEND
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=worker_config.WORKER_PREFETCH_MULTIPLIER,
)

async def _init_browser():
    """初始化全局浏览器实例"""
    global _playwright, _browser
    if _browser is None:
        logger.info("正在初始化全局 Playwright 浏览器实例...")
        _playwright = await async_playwright().start()
        
        browser_options = {
            "headless": worker_config.BROWSER_HEADLESS,
            "timeout": worker_config.BROWSER_TIMEOUT,
        }
        # 注意：这里我们启动一次浏览器，后续所有任务复用
        # 如果需要支持不同类型的浏览器（firefox, webkit），可能需要更复杂的逻辑
        _browser = await _playwright.chromium.launch(**browser_options)
        logger.info("全局 Playwright 浏览器实例初始化完成")

async def _close_browser():
    """关闭全局浏览器实例"""
    global _playwright, _browser
    if _browser:
        logger.info("正在关闭全局 Playwright 浏览器实例...")
        await _browser.close()
        _browser = None
    
    if _playwright:
        await _playwright.stop()
        _playwright = None

@worker_process_init.connect
def init_worker_process(**kwargs):
    """
    Worker 进程初始化信号处理
    
    在每个 Worker 子进程启动时初始化 Playwright 浏览器
    """
    # 异步初始化需要在事件循环中运行
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_init_browser())

@worker_process_shutdown.connect
def shutdown_worker_process(**kwargs):
    """
    Worker 进程关闭信号处理
    """
    # 尝试优雅关闭
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_close_browser())
    except Exception as e:
        logger.error(f"关闭浏览器实例时发生错误: {e}")

async def _crawl_page_async(
    url: str,
    options: Optional[Dict[str, Any]] = None,
    hook_scripts: Optional[list] = None
) -> Dict[str, Any]:
    """
    异步爬取页面（内部函数）
    
    Args:
        url: 目标 URL
        options: 爬取选项（代理、超时等）
        hook_scripts: 要注入的 JavaScript 钩子脚本列表
    
    Returns:
        包含 URL、HTML 内容和其他元信息的字典
    """
    global _browser
    
    options = options or {}
    hook_scripts = hook_scripts or []
    
    # 确保浏览器已初始化
    if _browser is None:
        logger.warning("浏览器实例未初始化，尝试重新初始化...")
        await _init_browser()
        if _browser is None:
             raise RuntimeError("无法初始化 Playwright 浏览器")

    # 配置代理
    proxy = None
    if options.get("proxy") or worker_config.PROXY_URL:
        proxy_config = {
            "server": options.get("proxy") or worker_config.PROXY_URL
        }
        if worker_config.PROXY_USERNAME and worker_config.PROXY_PASSWORD:
            proxy_config["username"] = worker_config.PROXY_USERNAME
            proxy_config["password"] = worker_config.PROXY_PASSWORD
        proxy = proxy_config
    
    # User-Agent 配置
    user_agent = options.get("user_agent")
    if not user_agent:
        # 默认使用通用浏览器 UA，或者后续从 UA 池中随机选择
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    context: Optional[BrowserContext] = None
    try:
        # 创建浏览器上下文
        context_options = {
            "user_agent": user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "device_scale_factor": 1,
        }
        if proxy:
            context_options["proxy"] = proxy
        
        # 为每个任务创建独立的上下文
        context = await _browser.new_context(**context_options)
        
        # 创建新页面
        page: Page = await context.new_page()
        
        # 注入钩子脚本
        for script in hook_scripts:
            try:
                await page.add_init_script(script)
                logger.debug(f"已注入钩子脚本: {script[:50]}...")
            except Exception as e:
                logger.warning(f"注入钩子脚本失败: {str(e)}")
        
        # 集成 playwright-stealth 反爬
        if HAS_STEALTH:
            await stealth_async(page)
            logger.debug("已启用 playwright-stealth 反爬模式")
        
        # 导航到目标 URL
        logger.info(f"开始爬取: {url}")
        
        # 使用 options 中的超时或默认超时
        timeout = options.get("timeout", worker_config.BROWSER_TIMEOUT)
        
        # 优化等待策略：默认 domcontentloaded，支持自定义选择器等待
        wait_until = options.get("wait_until", "domcontentloaded")
        wait_for_selector = options.get("wait_for_selector")
        
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        
        # 如果指定了选择器，则额外等待选择器出现
        if wait_for_selector:
            try:
                await page.wait_for_selector(wait_for_selector, timeout=timeout)
                logger.debug(f"已等待选择器: {wait_for_selector}")
            except Exception as e:
                logger.warning(f"等待选择器超时: {wait_for_selector}, error: {str(e)}")
        
        # 获取页面内容
        html_content = await page.content()
        
        # 获取页面元信息
        title = await page.title()
        url_final = page.url
        
        # 获取响应状态
        status_code = response.status if response else None
        
        result = {
            "url": url_final,
            "original_url": url,
            "status_code": status_code,
            "title": title,
            "html": html_content,
            "success": True,
        }
        
        logger.info(f"爬取成功: {url}, Status={status_code}")
        return result
        
    except Exception as e:
        logger.error(f"爬取失败: {url}, Error={str(e)}")
        raise
    finally:
        # 务必关闭上下文，释放资源，但不关闭 Browser
        if context:
            await context.close()


@celery_app.task(
    name="astra_farm.workers.playwright_worker.crawl_page",
    bind=True,
    max_retries=worker_config.MAX_RETRIES,
    default_retry_delay=worker_config.RETRY_DELAY,
    acks_late=True,
)
def crawl_page(
    self,
    url: str,
    options: Optional[Dict[str, Any]] = None,
    hook_scripts: Optional[list] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Celery 任务：爬取网页
    
    Args:1
        url: 目标 URL
        options: 爬取选项
        hook_scripts: 要注入的 JavaScript 钩子脚本
        **kwargs: 其他参数
    
    Returns:
        爬取结果字典
    """
    try:
        # 运行异步函数
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            _crawl_page_async(url, options, hook_scripts)
        )
        
        return result
        
    except Exception as exc:
        logger.error(
            f"任务执行失败 (尝试 {self.request.retries + 1}/{worker_config.MAX_RETRIES}): "
            f"URL={url}, Error={str(exc)}"
        )
        
        # 重试逻辑
        if self.request.retries < worker_config.MAX_RETRIES:
            raise self.retry(exc=exc)
        else:
            # 达到最大重试次数，返回错误结果
            return {
                "url": url,
                "success": False,
                "error": str(exc),
                "retries": self.request.retries,
            }
