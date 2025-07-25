"""
基础爬虫类

为sport模块等提供统一的基础爬虫架构
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from .logger import get_logger
from .http_client import HttpClient
from .utils import ensure_dir, save_to_csv, generate_timestamp_filename


class BaseScraper(ABC):
    """基础爬虫类"""
    
    def __init__(
        self,
        name: str,
        output_dir: str = 'output',
        delay_range: tuple = (1, 3),
        headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化基础爬虫
        
        Args:
            name: 爬虫名称
            output_dir: 输出目录
            delay_range: 请求延迟范围
            headers: 自定义请求头
        """
        self.name = name
        self.output_dir = output_dir
        
        # 确保输出目录存在
        ensure_dir(self.output_dir)
        
        # 设置日志
        self.logger = get_logger(f'scraper.{name}', self.output_dir)
        
        # 设置HTTP客户端
        self.http_client = HttpClient(
            headers=headers,
            delay_range=delay_range,
            logger=self.logger
        )
        
        # 存储爬取的数据
        self.data: List[Dict[str, Any]] = []
        
        self.logger.info(f"初始化爬虫: {name}")
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        抽象方法：执行爬虫逻辑
        
        Returns:
            爬取的数据列表
        """
        pass
    
    def save_data(
        self,
        data: Optional[List[Dict[str, Any]]] = None,
        filename: Optional[str] = None,
        format: str = 'xlsx'
    ) -> str:
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据，默认使用self.data
            filename: 文件名，默认自动生成
            format: 文件格式 ('xlsx', 'csv', 'json')
            
        Returns:
            保存的文件路径
        """
        if data is None:
            data = self.data
        
        if not data:
            self.logger.warning("没有数据需要保存")
            return ""
        
        if filename is None:
            filename = generate_timestamp_filename(
                prefix=self.name,
                extension=f'.{format}'
            )
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if format == 'xlsx':
                df = pd.DataFrame(data)
                df.to_excel(filepath, index=False)
            elif format == 'csv':
                save_to_csv(data, filepath)
            elif format == 'json':
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的文件格式: {format}")
            
            self.logger.info(f"数据已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return ""
    
    def run(self, save_format: str = 'xlsx') -> List[Dict[str, Any]]:
        """
        运行爬虫
        
        Args:
            save_format: 保存格式
            
        Returns:
            爬取的数据
        """
        self.logger.info(f"开始运行爬虫: {self.name}")
        
        try:
            # 执行爬虫逻辑
            self.data = self.scrape()
            
            # 保存数据
            if self.data:
                self.save_data(format=save_format)
                self.logger.info(f"爬虫运行完成，共获取 {len(self.data)} 条数据")
            else:
                self.logger.warning("未获取到任何数据")
            
            return self.data
            
        except Exception as e:
            self.logger.error(f"爬虫运行失败: {e}")
            return []
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'http_client'):
            self.http_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class SportScraper(BaseScraper):
    """体育数据爬虫基类"""
    
    def __init__(
        self,
        sport_name: str,
        sport_id: Optional[str] = None,
        output_dir: str = 'sport/output',
        **kwargs
    ):
        """
        初始化体育爬虫
        
        Args:
            sport_name: 体育项目名称
            sport_id: 体育项目ID
            output_dir: 输出目录
        """
        self.sport_name = sport_name
        self.sport_id = sport_id or sport_name.lower().replace(' ', '_')
        
        super().__init__(
            name=f"{self.sport_id}",
            output_dir=output_dir,
            **kwargs
        )
    
    def parse_competition_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        解析比赛数据的通用方法
        
        Args:
            html_content: HTML内容
            
        Returns:
            解析后的比赛数据列表
        """
        # 子类可以重写此方法实现特定的解析逻辑
        return []
    
    def get_competition_urls(self) -> List[str]:
        """
        获取比赛页面URL列表
        
        Returns:
            URL列表
        """
        # 子类可以重写此方法
        return []
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        默认的体育数据爬取流程
        """
        all_data = []
        
        urls = self.get_competition_urls()
        
        for url in urls:
            try:
                self.logger.info(f"正在爬取: {url}")
                response = self.http_client.get(url)
                
                # 解析数据
                data = self.parse_competition_data(response.text)
                all_data.extend(data)
                
                self.logger.info(f"从 {url} 获取到 {len(data)} 条数据")
                
            except Exception as e:
                self.logger.error(f"爬取 {url} 失败: {e}")
                continue
        
        return all_data