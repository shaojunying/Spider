"""
安居客房源信息爬虫 - 重构版本
使用公共模块的统一架构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 使用公共模块
from common import (
    get_logger, HttpClient, save_to_csv, load_json, save_json, 
    ensure_dir, normalize_price_text, parse_area_text
)
from config import communities, DEFAULT_INFO_PATH, DEFAULT_HISTORY_PATH, OUTPUT_PATH, COMMUNITY_NAME

# 配置日志
logger = get_logger('house_buy.anjuke', OUTPUT_PATH)


@dataclass
class HouseInfo:
    """房源信息数据类"""
    id: str
    community: str
    price_per_sqm: Optional[float] = None
    total_price: Optional[float] = None
    house_type: Optional[str] = None
    area: Optional[float] = None
    floor: Optional[str] = None
    orientation: Optional[str] = None
    decoration: Optional[str] = None
    year: Optional[str] = None
    property_type: Optional[str] = None
    title: Optional[str] = None
    tags: List[str] = None
    link: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            '小区': self.community,
            '单价': self.price_per_sqm,
            '报价': self.total_price,
            '户型': self.house_type,
            '建筑面积': self.area,
            '楼层': self.floor,
            '朝向': self.orientation,
            '装修': self.decoration,
            '年代': self.year,
            '类型': self.property_type,
            '标题': self.title,
            '标签': self.tags or [],
            'link': self.link
        }


class FileManager:
    """文件操作管理器 - 使用公共模块重构"""

    @staticmethod
    def load_csv(filename: str) -> List[Dict]:
        """加载CSV文件"""
        if not os.path.exists(filename):
            logger.info(f"文件 {filename} 不存在，返回空列表")
            return []

        try:
            import csv
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                logger.info(f"成功加载 {filename}，共 {len(data)} 条记录")
                return data
        except Exception as e:
            logger.error(f"加载文件 {filename} 失败: {e}")
            return []

    @staticmethod
    def save_csv(data: List[Dict], filename: str, fields: List[str]) -> bool:
        """保存数据到CSV文件"""
        try:
            save_to_csv(data, filename, fields)
            logger.info(f"成功保存 {len(data)} 条记录到 {filename}")
            return True
        except Exception as e:
            logger.error(f"保存文件 {filename} 失败: {e}")
            return False

    @staticmethod
    def load_json(filename: str) -> Dict:
        """加载JSON文件"""
        try:
            return load_json(filename)
        except Exception as e:
            logger.error(f"加载JSON文件 {filename} 失败: {e}")
            return {}

    @staticmethod
    def save_json(data: Dict, filename: str) -> bool:
        """保存数据到JSON文件"""
        try:
            save_json(data, filename)
            logger.info(f"成功保存数据到 {filename}")
            return True
        except Exception as e:
            logger.error(f"保存JSON文件 {filename} 失败: {e}")
            return False

    @staticmethod
    def append_csv(rows: List[Dict], filename: str, fields: List[str]) -> bool:
        """追加数据到CSV文件"""
        try:
            import csv
            file_exists = os.path.exists(filename)
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(rows)
            logger.info(f"成功追加 {len(rows)} 条记录到 {filename}")
            return True
        except Exception as e:
            logger.error(f"追加文件 {filename} 失败: {e}")
            return False


class DateHelper:
    """日期辅助工具"""

    @staticmethod
    def today() -> str:
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def yesterday() -> str:
        return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


class RateLimitHandler:
    """限流处理器"""

    @staticmethod
    def solve_anjuke_verification(url: str):
        """使用 Selenium 打开页面并处理点击验证"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        import time

        CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

        try:
            driver.get(url)
            logger.info("页面加载完成，等待用户手动完成验证...")
            
            # 等待用户手动完成验证，这里可以添加更智能的等待逻辑
            input("请在浏览器中完成验证，然后按回车键继续...")
            
            # 获取验证后的cookies
            cookies = driver.get_cookies()
            logger.info(f"获取到 {len(cookies)} 个cookies")
            
            return cookies
            
        except Exception as e:
            logger.error(f"处理验证失败: {e}")
            return None
        finally:
            driver.quit()


class DataProcessor:
    """数据处理器"""

    @staticmethod
    def parse_house_info(house_element, community_name: str, base_url: str) -> Optional[HouseInfo]:
        """解析房源信息"""
        try:
            # 提取房源ID
            house_id = house_element.get('house_id') or house_element.get('data-house_id', '')
            
            # 提取标题
            title_elem = house_element.select_one('.house-title a')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 提取链接
            link = urljoin(base_url, title_elem['href']) if title_elem else ''
            
            # 提取价格信息
            price_elem = house_element.select_one('.price-det strong')
            price_per_sqm = normalize_price_text(price_elem.get_text(strip=True)) if price_elem else None
            
            total_price_elem = house_element.select_one('.unit-price')
            total_price = normalize_price_text(total_price_elem.get_text(strip=True)) if total_price_elem else None
            
            # 提取房屋详情
            house_details = house_element.select_one('.details-item')
            house_type = ''
            area = None
            floor = ''
            orientation = ''
            decoration = ''
            year = ''
            
            if house_details:
                details_text = house_details.get_text(strip=True)
                details_parts = details_text.split('|')
                
                if len(details_parts) >= 1:
                    house_type = details_parts[0].strip()
                
                if len(details_parts) >= 2:
                    area = parse_area_text(details_parts[1].strip())
                
                if len(details_parts) >= 3:
                    floor = details_parts[2].strip()
                
                if len(details_parts) >= 4:
                    orientation = details_parts[3].strip()
                
                if len(details_parts) >= 5:
                    decoration = details_parts[4].strip()
                
                if len(details_parts) >= 6:
                    year = details_parts[5].strip()
            
            # 提取标签
            tag_elements = house_element.select('.tags-bottom .item-tags span')
            tags = [tag.get_text(strip=True) for tag in tag_elements]
            
            return HouseInfo(
                id=house_id,
                community=community_name,
                price_per_sqm=price_per_sqm,
                total_price=total_price,
                house_type=house_type,
                area=area,
                floor=floor,
                orientation=orientation,
                decoration=decoration,
                year=year,
                title=title,
                tags=tags,
                link=link
            )
            
        except Exception as e:
            logger.error(f"解析房源信息失败: {e}")
            return None


class AnjukeScraper:
    """安居客爬虫 - 重构版本"""
    
    def __init__(self):
        # 使用公共HTTP客户端
        self.http_client = HttpClient(
            delay_range=(2, 5),
            logger=logger
        )
        
        self.data_processor = DataProcessor()
        self.file_manager = FileManager()
        self.rate_limit_handler = RateLimitHandler()
        
        # 确保输出目录存在
        ensure_dir(OUTPUT_PATH)
    
    def scrape_community(self, community_name: str, community_url: str) -> List[HouseInfo]:
        """爬取单个小区的房源信息"""
        logger.info(f"开始爬取小区: {community_name}")
        houses = []
        
        try:
            response = self.http_client.get(community_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 检查是否遇到验证页面
            if "验证" in response.text or "verification" in response.text.lower():
                logger.warning("遇到验证页面，尝试使用Selenium处理")
                cookies = self.rate_limit_handler.solve_anjuke_verification(community_url)
                
                if cookies:
                    # 设置cookies后重新请求
                    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                    self.http_client.set_cookies(cookie_dict)
                    response = self.http_client.get(community_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析房源列表
            house_elements = soup.select('.house-item')
            
            for house_element in house_elements:
                house_info = self.data_processor.parse_house_info(
                    house_element, community_name, community_url
                )
                if house_info:
                    houses.append(house_info)
            
            logger.info(f"小区 {community_name} 爬取完成，共获取 {len(houses)} 条房源信息")
            
        except Exception as e:
            logger.error(f"爬取小区 {community_name} 失败: {e}")
        
        return houses
    
    def run(self):
        """运行爬虫"""
        logger.info("开始运行安居客爬虫")
        
        all_houses = []
        
        for community_name, community_url in communities.items():
            houses = self.scrape_community(community_name, community_url)
            all_houses.extend(houses)
        
        # 保存数据
        if all_houses:
            # 转换为字典格式
            houses_data = [house.to_dict() for house in all_houses]
            
            # 保存到CSV
            today = DateHelper.today()
            csv_filename = os.path.join(OUTPUT_PATH, f'houses_info_{today}.csv')
            
            fieldnames = list(houses_data[0].keys()) if houses_data else []
            self.file_manager.save_csv(houses_data, csv_filename, fieldnames)
            
            # 也保存一份不带日期的文件
            default_csv = os.path.join(OUTPUT_PATH, 'houses_info.csv')
            self.file_manager.save_csv(houses_data, default_csv, fieldnames)
            
            logger.info(f"爬虫运行完成，共获取 {len(all_houses)} 条房源信息")
        else:
            logger.warning("未获取到任何房源信息")
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'http_client'):
            self.http_client.close()


if __name__ == "__main__":
    scraper = AnjukeScraper()
    scraper.run()