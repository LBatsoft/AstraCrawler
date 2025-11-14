"""
数据提取器测试
"""
import pytest
from astra_dataflow.extractors.html_extractor import HTMLExtractor


def test_extract_text():
    """测试文本提取"""
    html = "<html><body><h1>标题</h1><p>段落内容</p></body></html>"
    extractor = HTMLExtractor(html)
    text = extractor.extract_text()
    assert "标题" in text
    assert "段落内容" in text


def test_extract_title():
    """测试标题提取"""
    html = "<html><head><title>测试标题</title></head><body></body></html>"
    extractor = HTMLExtractor(html)
    title = extractor.extract_title()
    assert title == "测试标题"


def test_extract_links():
    """测试链接提取"""
    html = '<html><body><a href="https://example.com">链接</a></body></html>'
    extractor = HTMLExtractor(html)
    links = extractor.extract_links()
    assert len(links) == 1
    assert links[0]["href"] == "https://example.com"
    assert links[0]["text"] == "链接"

