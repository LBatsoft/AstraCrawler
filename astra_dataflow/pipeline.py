"""
数据处理管道

整合提取、清洗和存储流程
"""
import logging
import json
import os
import time
from typing import Dict, Any, Optional
from .extractors.html_extractor import HTMLExtractor
from .cleaners.simple_cleaner import SimpleCleaner

logger = logging.getLogger(__name__)


class DataPipeline:
    """数据处理管道"""
    
    def __init__(
        self, 
        enable_cleaning: bool = True,
        storage_dir: str = "data/output"
    ):
        """
        初始化管道
        
        Args:
            enable_cleaning: 是否启用数据清洗
            storage_dir: 数据存储目录
        """
        self.enable_cleaning = enable_cleaning
        self.cleaner = SimpleCleaner() if enable_cleaning else None
        self.storage_dir = storage_dir
        
        # 确保存储目录存在
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
            
    def save_data(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        保存数据到本地文件 (JSONL格式)
        
        Args:
            data: 要保存的数据字典
            filename: 文件名（如果为None则自动生成）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            # 按日期生成文件名: 2023-10-27.jsonl
            date_str = time.strftime("%Y-%m-%d")
            filename = f"{date_str}.jsonl"
            
        filepath = os.path.join(self.storage_dir, filename)
        
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            logger.info(f"数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            raise

    def process(self, html: str, url: Optional[str] = None, hook_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        处理 HTML 内容
        
        Args:
            html: HTML 内容
            url: 页面 URL（用于提取绝对链接）
            hook_data: 提取到的 Hook 数据
        
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
            
            # 合并 Hook 数据
            if hook_data:
                data["hook_data"] = hook_data
            
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
                
            # 添加处理时间戳
            data["processed_at"] = time.time()
            
            # 自动保存数据
            self.save_data(data)
            
            logger.info(f"数据处理完成: URL={url}")
            return data
            
        except Exception as e:
            logger.error(f"数据处理失败: URL={url}, Error={str(e)}")
            raise
