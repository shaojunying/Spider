"""
通用工具函数模块

提供项目中常用的工具函数
"""

import os
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


def ensure_dir(path: Union[str, Path]) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        目录路径字符串
    """
    path_str = str(path)
    if not os.path.exists(path_str):
        os.makedirs(path_str, exist_ok=True)
    return path_str


def save_to_csv(
    data: List[Dict[str, Any]],
    filename: str,
    fieldnames: Optional[List[str]] = None,
    encoding: str = 'utf-8-sig'
) -> None:
    """
    保存数据到CSV文件
    
    Args:
        data: 要保存的数据列表
        filename: 文件名
        fieldnames: 字段名列表，如果为None则使用第一行数据的键
        encoding: 文件编码
    """
    if not data:
        return
    
    # 确保目录存在
    ensure_dir(os.path.dirname(filename) or '.')
    
    if fieldnames is None:
        fieldnames = list(data[0].keys()) if data else []
    
    with open(filename, 'w', newline='', encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_json(filename: str, encoding: str = 'utf-8') -> Union[Dict, List]:
    """
    从JSON文件加载数据
    
    Args:
        filename: 文件名
        encoding: 文件编码
        
    Returns:
        JSON数据
    """
    with open(filename, 'r', encoding=encoding) as f:
        return json.load(f)


def save_json(
    data: Union[Dict, List],
    filename: str,
    encoding: str = 'utf-8',
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    保存数据到JSON文件
    
    Args:
        data: 要保存的数据
        filename: 文件名
        encoding: 文件编码
        indent: 缩进
        ensure_ascii: 是否确保ASCII编码
    """
    # 确保目录存在
    ensure_dir(os.path.dirname(filename) or '.')
    
    with open(filename, 'w', encoding=encoding) as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '_', filename)
    
    # 移除首尾空格和点
    cleaned = cleaned.strip(' .')
    
    # 限制长度
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    
    return cleaned


def extract_numbers(text: str) -> List[float]:
    """
    从文本中提取数字
    
    Args:
        text: 输入文本
        
    Returns:
        提取到的数字列表
    """
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches if match]


def generate_timestamp_filename(
    prefix: str = '',
    suffix: str = '',
    extension: str = '.txt',
    date_format: str = '%Y%m%d_%H%M%S'
) -> str:
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        suffix: 文件名后缀
        extension: 文件扩展名
        date_format: 日期格式
        
    Returns:
        带时间戳的文件名
    """
    timestamp = datetime.now().strftime(date_format)
    parts = [part for part in [prefix, timestamp, suffix] if part]
    return '_'.join(parts) + extension


def split_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分割成指定大小的块
    
    Args:
        lst: 要分割的列表
        chunk_size: 每块的大小
        
    Returns:
        分割后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_on_exception(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        delay: 重试间隔
        exceptions: 需要重试的异常类型
    """
    def decorator(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    import time
                    time.sleep(delay)
                    continue
                else:
                    raise last_exception
    
    return decorator


def normalize_price_text(price_text: str) -> Optional[float]:
    """
    标准化价格文本，提取数字
    
    Args:
        price_text: 价格文本
        
    Returns:
        提取到的价格数字，失败返回None
    """
    if not price_text:
        return None
    
    # 移除常见的价格单位和符号
    cleaned = re.sub(r'[￥¥$,，万元]', '', price_text)
    
    # 提取数字
    numbers = extract_numbers(cleaned)
    
    if numbers:
        price = numbers[0]
        # 如果原文本包含"万"，则乘以10000
        if '万' in price_text:
            price *= 10000
        return price
    
    return None


def parse_area_text(area_text: str) -> Optional[float]:
    """
    解析面积文本
    
    Args:
        area_text: 面积文本
        
    Returns:
        面积数字，失败返回None
    """
    if not area_text:
        return None
    
    # 移除单位
    cleaned = re.sub(r'[㎡平方米m²]', '', area_text)
    numbers = extract_numbers(cleaned)
    
    return numbers[0] if numbers else None