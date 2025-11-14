"""
数据清洗器测试
"""
import pytest
from astra_dataflow.cleaners.simple_cleaner import SimpleCleaner


def test_remove_whitespace():
    """测试移除空白字符"""
    text = "  这是   一个   测试   "
    cleaned = SimpleCleaner.remove_whitespace(text)
    assert cleaned == "这是 一个 测试"


def test_clean_all():
    """测试完整清洗流程"""
    text = "  这是   一个   测试  \n\t  "
    cleaned = SimpleCleaner.clean_all(text)
    assert "  " not in cleaned
    assert cleaned.strip() == cleaned

