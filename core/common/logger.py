"""
统一的日志配置模块

提供项目中所有爬虫脚本的统一日志配置
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logging(
    name: str = __name__,
    log_dir: str = 'logs',
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        log_level: 日志级别
        log_to_file: 是否输出到文件
        log_to_console: 是否输出到控制台
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
        
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handlers = []
    
    # 文件处理器
    if log_to_file:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(
            log_dir, 
            f'{name.replace(".", "_")}_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    # 添加处理器
    for handler in handlers:
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str, log_dir: str = 'logs') -> logging.Logger:
    """
    获取日志记录器的便捷方法
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        
    Returns:
        日志记录器
    """
    return setup_logging(name=name, log_dir=log_dir)


# 为向后兼容提供的快捷函数
def get_scraper_logger(script_name: str, output_dir: str = 'output') -> logging.Logger:
    """
    为爬虫脚本获取日志记录器
    """
    log_dir = os.path.join(output_dir, 'logs') if output_dir != 'logs' else output_dir
    return get_logger(f'scraper.{script_name}', log_dir)