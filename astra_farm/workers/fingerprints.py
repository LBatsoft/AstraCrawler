"""
指纹数据库模块

提供真实的浏览器指纹数据组合，确保 UA、硬件并发数、内存等特征的一致性。
"""
import random
from typing import Dict, Any, List

# 指纹数据结构定义
# {
#     "os": "Windows" | "Mac" | "Linux",
#     "ua": str,
#     "platform": str,
#     "hardwareConcurrency": int,
#     "deviceMemory": int,
#     "vendor": str,
#     "renderer": str,
#     "screen": {"width": int, "height": int}
# }

FINGERPRINTS: List[Dict[str, Any]] = [
    # Windows Desktop - High End
    {
        "os": "Windows",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "Win32",
        "hardwareConcurrency": 16,
        "deviceMemory": 16, # 16GB+
        "vendor": "Google Inc. (NVIDIA)",
        "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "screen": {"width": 1920, "height": 1080}
    },
    # Windows Desktop - Mid Range
    {
        "os": "Windows",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "platform": "Win32",
        "hardwareConcurrency": 8,
        "deviceMemory": 8,
        "vendor": "Google Inc. (Intel)",
        "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "screen": {"width": 1366, "height": 768}
    },
    # Mac Desktop (M1/M2)
    {
        "os": "Mac",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "platform": "MacIntel",
        "hardwareConcurrency": 8,
        "deviceMemory": 8,
        "vendor": "Google Inc. (Apple)",
        "renderer": "ANGLE (Apple, Apple M1, OpenGL 4.1)",
        "screen": {"width": 1440, "height": 900}
    },
    # Mac Desktop (Intel High End)
    {
        "os": "Mac",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "platform": "MacIntel",
        "hardwareConcurrency": 12,
        "deviceMemory": 32,
        "vendor": "Google Inc. (AMD)",
        "renderer": "ANGLE (AMD, AMD Radeon Pro 5500M, OpenGL 4.1)",
        "screen": {"width": 2560, "height": 1440}
    }
]

def get_random_fingerprint() -> Dict[str, Any]:
    """随机获取一个指纹配置"""
    return random.choice(FINGERPRINTS)

