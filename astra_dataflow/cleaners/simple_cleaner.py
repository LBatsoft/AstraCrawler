"""
简单数据清洗器

提供基础的文本清洗功能
"""
import re
from typing import Optional


class SimpleCleaner:
    """简单数据清洗器"""
    
    @staticmethod
    def remove_whitespace(text: str) -> str:
        """
        移除多余空白字符
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        # 替换多个空白字符为单个空格
        text = re.sub(r"\s+", " ", text)
        # 移除首尾空白
        return text.strip()
    
    @staticmethod
    def remove_special_chars(text: str, keep_chars: Optional[str] = None) -> str:
        """
        移除特殊字符
        
        Args:
            text: 原始文本
            keep_chars: 要保留的字符集合（正则表达式字符类）
        
        Returns:
            清洗后的文本
        """
        if keep_chars:
            # 只保留指定字符
            pattern = f"[^{keep_chars}]"
        else:
            # 默认保留字母、数字、中文、常见标点
            pattern = r"[^\w\s\u4e00-\u9fff，。！？；：、""''（）【】《》]"
        
        return re.sub(pattern, "", text)
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        标准化 Unicode 字符
        
        Args:
            text: 原始文本
        
        Returns:
            标准化后的文本
        """
        import unicodedata
        # 标准化为 NFC 形式
        return unicodedata.normalize("NFC", text)
    
    @staticmethod
    def remove_control_chars(text: str) -> str:
        """
        移除控制字符
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        # 移除控制字符（保留换行符和制表符）
        return re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    
    @staticmethod
    def clean_html_entities(text: str) -> str:
        """
        清理 HTML 实体
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        import html
        return html.unescape(text)
    
    @staticmethod
    def clean_all(text: str) -> str:
        """
        执行所有清洗步骤
        
        Args:
            text: 原始文本
        
        Returns:
            完全清洗后的文本
        """
        text = SimpleCleaner.clean_html_entities(text)
        text = SimpleCleaner.normalize_unicode(text)
        text = SimpleCleaner.remove_control_chars(text)
        text = SimpleCleaner.remove_whitespace(text)
        return text

