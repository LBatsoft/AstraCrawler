"""
HTML 内容提取器

使用 BeautifulSoup 提取网页可见文本和结构化数据
"""
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag, NavigableString


class HTMLExtractor:
    """HTML 内容提取器"""
    
    def __init__(self, html: str, parser: str = "lxml"):
        """
        初始化提取器
        
        Args:
            html: HTML 内容
            parser: BeautifulSoup 解析器，可选值: "lxml", "html.parser", "html5lib"
        """
        self.soup = BeautifulSoup(html, parser)
    
    def extract_text(self, remove_scripts: bool = True, remove_styles: bool = True) -> str:
        """
        提取可见文本内容
        
        Args:
            remove_scripts: 是否移除 script 标签
            remove_styles: 是否移除 style 标签
        
        Returns:
            提取的文本内容
        """
        # 创建副本以避免修改原始 soup
        soup = BeautifulSoup(str(self.soup), "html.parser")
        
        # 移除脚本和样式
        if remove_scripts:
            for script in soup(["script", "noscript"]):
                script.decompose()
        
        if remove_styles:
            for style in soup(["style"]):
                style.decompose()
        
        # 获取文本
        text = soup.get_text(separator=" ", strip=True)
        
        # 清理多余空白
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
    
    def extract_title(self) -> Optional[str]:
        """提取页面标题"""
        title_tag = self.soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else None
    
    def extract_meta(self) -> Dict[str, str]:
        """提取 meta 标签信息"""
        meta_data = {}
        
        # 提取 meta name
        for meta in self.soup.find_all("meta", attrs={"name": True}):
            name = meta.get("name")
            content = meta.get("content")
            if name and content:
                meta_data[name] = content
        
        # 提取 meta property (Open Graph)
        for meta in self.soup.find_all("meta", attrs={"property": True}):
            property_name = meta.get("property")
            content = meta.get("content")
            if property_name and content:
                meta_data[property_name] = content
        
        return meta_data
    
    def extract_links(self, absolute: bool = False, base_url: Optional[str] = None) -> List[Dict[str, str]]:
        """
        提取所有链接
        
        Args:
            absolute: 是否转换为绝对 URL
            base_url: 基础 URL，用于转换为绝对 URL
        
        Returns:
            链接列表，每个链接包含 href 和 text
        """
        links = []
        
        for link in self.soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            
            # 转换为绝对 URL
            if absolute and base_url:
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            
            links.append({
                "href": href,
                "text": text
            })
        
        return links
    
    def extract_images(self, absolute: bool = False, base_url: Optional[str] = None) -> List[Dict[str, str]]:
        """
        提取所有图片
        
        Args:
            absolute: 是否转换为绝对 URL
            base_url: 基础 URL
        
        Returns:
            图片列表，每个图片包含 src 和 alt
        """
        images = []
        
        for img in self.soup.find_all("img", src=True):
            src = img["src"]
            alt = img.get("alt", "")
            
            if absolute and base_url:
                from urllib.parse import urljoin
                src = urljoin(base_url, src)
            
            images.append({
                "src": src,
                "alt": alt
            })
        
        return images
    
    def extract_tables(self) -> List[List[List[str]]]:
        """
        提取表格数据
        
        Returns:
            表格列表，每个表格是二维列表
        """
        tables = []
        
        for table in self.soup.find_all("table"):
            table_data = []
            
            for row in table.find_all("tr"):
                row_data = []
                for cell in row.find_all(["td", "th"]):
                    cell_text = cell.get_text(strip=True)
                    row_data.append(cell_text)
                
                if row_data:
                    table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def extract_json_ld(self) -> List[Dict[str, Any]]:
        """
        提取 JSON-LD 结构化数据
        
        Returns:
            JSON-LD 数据列表
        """
        import json
        
        json_ld_data = []
        
        for script in self.soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return json_ld_data
    
    def extract_all(self) -> Dict[str, Any]:
        """
        提取所有可用数据
        
        Returns:
            包含所有提取数据的字典
        """
        return {
            "title": self.extract_title(),
            "text": self.extract_text(),
            "meta": self.extract_meta(),
            "links": self.extract_links(),
            "images": self.extract_images(),
            "tables": self.extract_tables(),
            "json_ld": self.extract_json_ld(),
        }

