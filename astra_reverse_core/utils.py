"""
逆向模块工具函数

用于加载和管理 JavaScript 钩子脚本
"""
import os
from pathlib import Path
from typing import List, Optional


def get_hook_script_path(script_name: str) -> Path:
    """
    获取钩子脚本文件路径
    
    Args:
        script_name: 脚本文件名（如 "hook_engine.js"）
    
    Returns:
        脚本文件的 Path 对象
    """
    current_dir = Path(__file__).parent
    script_path = current_dir / script_name
    
    if not script_path.exists():
        raise FileNotFoundError(f"钩子脚本不存在: {script_path}")
    
    return script_path


def load_hook_script(script_name: str) -> str:
    """
    加载钩子脚本内容
    
    Args:
        script_name: 脚本文件名
    
    Returns:
        脚本内容字符串
    """
    script_path = get_hook_script_path(script_name)
    return script_path.read_text(encoding="utf-8")


def get_default_hooks() -> List[str]:
    """
    获取默认钩子脚本列表
    
    Returns:
        默认钩子脚本内容列表
    """
    default_scripts = [
        "hook_engine.js",
        "ws_interceptor.js",
        "signature_hook.js",
    ]
    
    hooks = []
    for script_name in default_scripts:
        try:
            hooks.append(load_hook_script(script_name))
        except FileNotFoundError:
            # 如果脚本不存在，跳过
            pass
    
    return hooks


def get_jsrpc_hooks() -> List[str]:
    """
    获取 JsRpc 相关钩子脚本列表
    
    Returns:
        JsRpc 钩子脚本内容列表
    """
    jsrpc_scripts = [
        "jsrpc_client.js",
    ]
    
    hooks = []
    for script_name in jsrpc_scripts:
        try:
            hooks.append(load_hook_script(script_name))
        except FileNotFoundError:
            # 如果脚本不存在，跳过
            pass
    
    return hooks


def get_custom_hook(script_path: str) -> str:
    """
    加载自定义钩子脚本
    
    Args:
        script_path: 自定义脚本路径
    
    Returns:
        脚本内容字符串
    """
    path = Path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"自定义脚本不存在: {script_path}")
    
    return path.read_text(encoding="utf-8")

