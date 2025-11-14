"""
Playwright Worker 模块

使用 Playwright 执行网页爬取任务
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from celery import Celery
from celery.exceptions import Retry
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..config import worker_config

# 配置日志
logger = logging.getLogger(__name__)

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
    options = options or {}
    hook_scripts = hook_scripts or []
    
    # 配置浏览器选项
    browser_options = {
        "headless": options.get("headless", worker_config.BROWSER_HEADLESS),
        "timeout": options.get("timeout", worker_config.BROWSER_TIMEOUT),
    }
    
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
    
    async with async_playwright() as p:
        # 启动浏览器
        browser: Browser = await p.chromium.launch(**browser_options)
        
        try:
            # 创建浏览器上下文
            context_options = {}
            if proxy:
                context_options["proxy"] = proxy
            
            context: BrowserContext = await browser.new_context(**context_options)
            
            # 创建新页面
            page: Page = await context.new_page()
            
            # 注入钩子脚本
            for script in hook_scripts:
                try:
                    await page.add_init_script(script)
                    logger.debug(f"已注入钩子脚本: {script[:50]}...")
                except Exception as e:
                    logger.warning(f"注入钩子脚本失败: {str(e)}")
            
            # 导航到目标 URL
            logger.info(f"开始爬取: {url}")
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待页面加载完成
            await page.wait_for_load_state("domcontentloaded")
            
            # 获取页面内容
            html_content = await page.content()
            
            # 获取页面元信息
            title = await page.title()
            url_final = page.url
            
            # 获取响应状态
            status_code = response.status if response else None
            
            # 关闭上下文和浏览器
            await context.close()
            await browser.close()
            
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
            await browser.close()
            raise


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
    
    Args:
        self: Celery 任务实例（bind=True）
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

