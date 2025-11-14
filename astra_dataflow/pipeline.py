"""
数据处理管道

整合提取、清洗和存储流程
"""
import logging
from typing import Dict, Any, Optional
from .extractors.html_extractor import HTMLExtractor
from .cleaners.simple_cleaner import SimpleCleaner

logger = logging.getLogger(__name__)


class DataPipeline:
    """数据处理管道"""
    
    def __init__(self, enable_cleaning: bool = True):
        """
        初始化管道
        
        Args:
            enable_cleaning: 是否启用数据清洗
        """
        self.enable_cleaning = enable_cleaning
        self.cleaner = SimpleCleaner() if enable_cleaning else None
    
    def process(self, html: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        处理 HTML 内容
        
        Args:
            html: HTML 内容
            url: 页面 URL（用于提取绝对链接）
        
        Returns:
            处理后的数据字典
        """
        try:
            # 提取数据
            extractor = HTMLExtractor(html)
            data = extractor.extract_all()
            
            # 清洗文本数据
            if self.enable_cleaning and self.cleaner:
                if data.get("text"):
                    data["text"] = self.cleaner.clean_all(data["text"])
                
                # 清洗链接文本
                if data.get("links"):
                    for link in data["links"]:
                        if link.get("text"):
                            link["text"] = self.cleaner.clean_all(link["text"])
            
            # 添加 URL 信息
            if url:
                data["url"] = url
                # 转换为绝对链接
                if data.get("links"):
                    extractor_base = HTMLExtractor(html)
                    data["links"] = extractor_base.extract_links(absolute=True, base_url=url)
                if data.get("images"):
                    extractor_base = HTMLExtractor(html)
                    data["images"] = extractor_base.extract_images(absolute=True, base_url=url)
            
            logger.info(f"数据处理完成: URL={url}")
            return data
            
        except Exception as e:
            logger.error(f"数据处理失败: URL={url}, Error={str(e)}")
            raise

