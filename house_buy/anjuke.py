import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin
import csv
import re
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import communities, DEFAULT_INFO_PATH, DEFAULT_HISTORY_PATH, OUTPUT_PATH, COMMUNITY_NAME

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
    """文件操作管理器"""

    @staticmethod
    def load_csv(filename: str) -> List[Dict]:
        """加载CSV文件"""
        if not os.path.exists(filename):
            logger.info(f"文件 {filename} 不存在，返回空列表")
            return []

        try:
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
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"成功保存 {len(data)} 条记录到 {filename}")
            return True
        except Exception as e:
            logger.error(f"保存文件 {filename} 失败: {e}")
            return False

    @staticmethod
    def append_csv(rows: List[Dict], filename: str, fields: List[str]) -> bool:
        """追加数据到CSV文件"""
        try:
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
    def handle_rate_limit():
        """处理IP限流"""
        logger.warning("遇到IP限流机制")
        print("遇到IP限流机制，请手动打开以下链接继续抓取：")
        print(
            "https://m.anjuke.com/bj/sale/S3449979172707338/?isauction=221&position=1&kwtype=comm_one&now_time=1752151592&epauction&stats_key=1cc0e8bf-588f-49e2-94a2-94ea665a2258_1&from=Exp_Anjuke_Prop_List")
        print("请在浏览器中打开链接，等待页面加载完成后按回车继续抓取...")
        input("按回车继续...")


class HouseDetailParser:
    """房源详情解析器"""

    @staticmethod
    def safe_get_text(element) -> Optional[str]:
        """安全获取元素文本"""
        return element.text.strip() if element else None

    @staticmethod
    def extract_price(price_text: str) -> Optional[float]:
        """提取价格数字"""
        if not price_text:
            return None
        try:
            # 移除单位和空格，提取数字
            cleaned = re.sub(r'[^\d.]', '', price_text)
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    @staticmethod
    def extract_house_id(detail_url: str) -> Optional[str]:
        """从URL提取房源ID"""
        match = re.search(r'/bj/sale/([^/?]+)', detail_url)
        return match.group(1) if match else None

    @classmethod
    def parse_detail_page(cls, html: str, detail_url: str) -> Optional[HouseInfo]:
        """解析房源详情页"""
        if not html:
            return None

        house_id = cls.extract_house_id(detail_url)
        if not house_id:
            logger.warning(f"无法从URL提取房源ID: {detail_url}")
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # 基本信息提取
            community_name = cls.safe_get_text(
                soup.select_one("ul.houseinfo-list li:-soup-contains('小区') span.text")
            )

            # 单价
            price_per_sqm_elem = cls.safe_get_text(
                soup.select_one("ul.houseinfo-list div:has(span:-soup-contains('单价')) span.text")
            )
            price_per_sqm = cls.extract_price(price_per_sqm_elem)

            # 总价
            price_elem = cls.safe_get_text(soup.select_one(".baseinfo-dj span.baseinfo-num"))
            total_price = cls.extract_price(price_elem)

            # 户型
            house_type_spans = soup.select("div.baseinfo-data div:has(p:-soup-contains('户型')) span")
            house_type = "".join(span.get_text(strip=True) for span in house_type_spans)

            # 建筑面积
            area_text = cls.safe_get_text(
                soup.select_one("div.baseinfo-data div:has(p:-soup-contains('建筑面积')) span.baseinfo-num")
            )
            area = cls.extract_price(area_text)

            # 其他信息
            floor = cls.safe_get_text(soup.select_one("ul.houseinfo-list li:-soup-contains('楼层') span.text"))
            orientation = cls.safe_get_text(soup.select_one("ul.houseinfo-list li:-soup-contains('朝向') span.text"))
            decoration = cls.safe_get_text(soup.select_one("ul.houseinfo-list li:-soup-contains('装修') span.text"))
            year = cls.safe_get_text(soup.select_one("ul.houseinfo-list li:-soup-contains('年代') span.text"))
            property_type = cls.safe_get_text(soup.select_one("ul.houseinfo-list li:-soup-contains('类型') span.text"))
            title = cls.safe_get_text(soup.select_one("h1"))

            # 标签
            tags = [elem.text for elem in soup.select("ul.houseinfo-labels li.label")]

            house_info = HouseInfo(
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
                property_type=property_type,
                title=title,
                tags=tags,
                link=detail_url
            )

            logger.debug(f"解析房源成功: {house_id} - {community_name}")
            return house_info

        except Exception as e:
            logger.error(f"解析详情页失败 {detail_url}: {e}")
            return None


class AnjukeScraper:
    """安居客爬虫主类"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.anjuke.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.houses_data: List[HouseInfo] = []
        self.parser = HouseDetailParser()

    def get_page_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                logger.debug(f"成功获取页面: {url}")
                return response.text
            except requests.RequestException as e:
                logger.warning(f"请求失败（第 {attempt + 1} 次）: {url} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 4))

        logger.error(f"请求完全失败: {url}")
        return None

    def extract_house_links(self, html_content: str) -> List[str]:
        """提取房源链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.select('div[class*="house-item"], li[class*="item"], article')

        links = []
        for element in elements:
            link_elem = element.find('a', href=True)
            if link_elem:
                full_link = urljoin('https://m.anjuke.com', link_elem['href'])
                links.append(full_link)

        return links

    def is_target_community(self, house_info: HouseInfo, target_community: str) -> bool:
        """检查是否为目标小区"""
        return (house_info.community and
                house_info.community.strip() == target_community.strip())

    def scrape_community_page(self, community_name: str, page_url: str) -> Tuple[List[HouseInfo], bool]:
        """抓取单个页面的房源信息"""
        html_content = self.get_page_content(page_url)
        if not html_content:
            logger.error(f"获取页面内容失败: {page_url}")
            return [], False

        house_links = self.extract_house_links(html_content)
        if not house_links:
            logger.warning(f"页面未找到房源链接: {page_url}")
            return [], False

        logger.info(f"在页面找到 {len(house_links)} 个房源链接")

        matched_houses = []
        unmatched_count = 0

        for i, link in enumerate(house_links, 1):
            logger.debug(f"处理房源 {i}/{len(house_links)}: {link}")

            detail_html = self.get_page_content(link)
            if not detail_html:
                logger.warning(f"获取详情页失败: {link}")
                continue

            house_info = self.parser.parse_detail_page(detail_html, link)
            if not house_info:
                logger.warning(f"解析详情页失败: {link}")
                continue

            if self.is_target_community(house_info, community_name):
                matched_houses.append(house_info)
                unmatched_count = 0
                logger.info(f"✓ 匹配房源: {house_info.id} - {house_info.community} - "
                            f"单价{house_info.price_per_sqm} - 总价{house_info.total_price}")
            else:
                unmatched_count += 1
                logger.debug(f"✗ 跳过房源: {house_info.community} (目标: {community_name})")

                if unmatched_count >= 4:
                    logger.warning("连续4个房源不匹配，停止当前页面抓取")
                    return matched_houses, True

        return matched_houses, True

    def scrape_by_community(self, community_name: str, community_id: str, max_pages: int = 5):
        """按小区抓取房源"""
        logger.info(f"开始抓取小区: {community_name} (ID: {community_id})")

        base_url = f"https://m.anjuke.com/bj/sale/?comm_id={community_id}"
        total_collected = 0

        max_pages = 1
        for page in range(1, max_pages + 1):
            logger.info(f"正在抓取第 {page} 页...")

            page_url = base_url if page == 1 else f"{base_url}&page={page}"
            matched_houses, should_continue = self.scrape_community_page(community_name, page_url)

            if not matched_houses:
                if not should_continue:
                    RateLimitHandler.handle_rate_limit()
                    continue
                else:
                    logger.warning(f"第 {page} 页没有匹配的房源")
                    break

            self.houses_data.extend(matched_houses)
            total_collected += len(matched_houses)
            logger.info(f"第 {page} 页收集到 {len(matched_houses)} 个房源")

            if not should_continue:
                break

            # 页面间隔
            time.sleep(random.uniform(2, 4))

        logger.info(f"小区 {community_name} 抓取完成，共收集 {total_collected} 个房源")

    def get_houses_as_dicts(self) -> List[Dict]:
        """获取房源数据的字典格式"""
        return [house.to_dict() for house in self.houses_data]

    def save_to_json(self, filename: str = 'anjuke_filtered.json'):
        """保存为JSON文件"""
        data = self.get_houses_as_dicts()
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")


class DataProcessor:
    """数据处理器"""

    @staticmethod
    def merge_house_data(new_data: List[Dict], history_data: List[Dict],
                         price_history_data: List[Dict] = None) -> List[Dict]:
        """合并新数据和历史数据，并计算价格统计信息"""
        history_map = {h.get('id') or h.get('house_id', ''): h for h in history_data}

        # 构建价格历史映射
        price_stats = {}
        if price_history_data:
            for record in price_history_data:
                house_id = record.get('id', '')
                if not house_id:
                    continue

                price_str = record.get('单价', '')
                date_str = record.get('日期', '')

                # 尝试解析价格
                try:
                    price = float(price_str) if price_str else None
                except (ValueError, TypeError):
                    price = None

                if price is not None and date_str:
                    if house_id not in price_stats:
                        price_stats[house_id] = []
                    price_stats[house_id].append({
                        'price': price,
                        'date': date_str
                    })

        # 合并数据并计算价格统计
        for house in new_data:
            house_id = house.get('id', '')
            if not house_id:
                continue

            # 基础数据合并
            if house_id in history_map:
                history_map[house_id].update(house)
            else:
                history_map[house_id] = house

            # 计算价格统计
            current_house = history_map[house_id]

            # 获取当前价格
            current_price = current_house.get('单价')
            try:
                current_price = float(current_price) if current_price else None
            except (ValueError, TypeError):
                current_price = None

            # 初始化价格统计字段
            current_house.update({
                '最高价': None,
                '最高价日期': None,
                '最低价': None,
                '最低价日期': None,
                '最新房价日期': DateHelper.today()
            })

            # 如果有价格历史数据，计算统计信息
            if house_id in price_stats:
                price_records = price_stats[house_id]

                # 添加当前价格到历史记录中进行比较
                if current_price is not None:
                    price_records.append({
                        'price': current_price,
                        'date': DateHelper.today()
                    })

                if price_records:
                    # 找出最高价和最低价
                    max_record = max(price_records, key=lambda x: x['price'])
                    min_record = min(price_records, key=lambda x: x['price'])

                    # 找出最新价格日期
                    latest_record = max(price_records, key=lambda x: x['date'])

                    current_house.update({
                        '最高价': max_record['price'],
                        '最高价日期': max_record['date'],
                        '最低价': min_record['price'],
                        '最低价日期': min_record['date'],
                        '最新房价日期': latest_record['date']
                    })
            else:
                # 没有历史数据时，如果有当前价格，则当前价格就是最高价和最低价
                if current_price is not None:
                    today_str = DateHelper.today()
                    current_house.update({
                        '最高价': current_price,
                        '最高价日期': today_str,
                        '最低价': current_price,
                        '最低价日期': today_str,
                        '最新房价日期': today_str
                    })

        return list(history_map.values())

    @staticmethod
    def create_price_history(houses_data: List[Dict], existing_history: List[Dict]) -> List[Dict]:
        """创建价格历史记录"""
        today_str = DateHelper.today()

        # 过滤掉今天的记录
        filtered_history = [row for row in existing_history if row.get('日期') != today_str]

        # 构建历史价格映射
        price_map = {}
        for row in filtered_history:
            house_id = row.get('id', '')
            if house_id:
                price_map[house_id] = row.get('单价', '')

        # 添加今天的记录
        for house in houses_data:
            house_id = house.get('id', '')
            if house_id:
                old_price = price_map.get(house_id, '')
                filtered_history.append({
                    'id': house_id,
                    '小区': house.get('小区', ''),
                    '日期': today_str,
                    '单价': house.get('单价', ''),
                    '旧单价': old_price
                })

        return filtered_history


def main():
    """主函数"""
    logger.info("开始执行安居客房源抓取任务")

    scraper = AnjukeScraper()
    file_manager = FileManager()
    data_processor = DataProcessor()

    # 抓取所有小区
    for community in communities:
        comm_id = community.get('comm_id')
        comm_name = community.get('name')

        if not comm_id:
            logger.warning(f"小区 {comm_name} 缺少 comm_id，跳过")
            continue

        scraper.scrape_by_community(comm_name, comm_id, max_pages=5)

    # 处理数据
    new_houses_data = scraper.get_houses_as_dicts()
    if not new_houses_data:
        logger.warning("没有抓取到任何房源数据")
        return

    # 合并历史数据
    history_data = file_manager.load_csv(DEFAULT_INFO_PATH)
    price_history_data = file_manager.load_csv(DEFAULT_HISTORY_PATH)
    merged_data = data_processor.merge_house_data(new_houses_data, history_data, price_history_data)

    # 保存房源数据
    today_str = DateHelper.today()
    fields = list(merged_data[0].keys()) if merged_data else []

    file_manager.save_csv(merged_data, os.path.join(OUTPUT_PATH, f'houses_info_{today_str}.csv'), fields)
    file_manager.save_csv(merged_data, DEFAULT_INFO_PATH, fields)

    # 处理价格历史
    price_history_fields = ['id', '小区', '日期', '单价', '旧单价']
    existing_price_history = file_manager.load_csv(DEFAULT_HISTORY_PATH)
    new_price_history = data_processor.create_price_history(new_houses_data, existing_price_history)

    file_manager.save_csv(new_price_history, os.path.join(OUTPUT_PATH,f'price_history_{today_str}.csv'), price_history_fields)
    file_manager.save_csv(new_price_history, DEFAULT_HISTORY_PATH, price_history_fields)

    logger.info("开始数据分析")

    from house_analysis import analyze_house_changes
    analyze_house_changes(DEFAULT_HISTORY_PATH, DEFAULT_INFO_PATH, community=COMMUNITY_NAME)

    logger.info("任务完成")


if __name__ == "__main__":
    main()