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
            
            # 优化：直接在提取时处理 URL 转换，避免重复调用 extractor 方法造成多次 DOM 遍历
            # 我们通过组合方式手动调用需要的方法，而不是使用 extract_all
            
            data = {
                "title": extractor.extract_title(),
                "text": extractor.extract_text(),
                "meta": extractor.extract_meta(),
                "links": extractor.extract_links(absolute=True, base_url=url) if url else extractor.extract_links(),
                "images": extractor.extract_images(absolute=True, base_url=url) if url else extractor.extract_images(),
                "tables": extractor.extract_tables(),
                "json_ld": extractor.extract_json_ld(),
            }
            
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
            
            logger.info(f"数据处理完成: URL={url}")
            return data
            
        except Exception as e:
            logger.error(f"数据处理失败: URL={url}, Error={str(e)}")
            raise
