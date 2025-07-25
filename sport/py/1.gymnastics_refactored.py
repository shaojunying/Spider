"""
体操比赛数据爬虫 - 重构版本
使用公共模块的统一架构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Any
from common.base_scraper import SportScraper


class GymnasticsScraper(SportScraper):
    """体操比赛数据爬虫"""
    
    def __init__(self):
        super().__init__(
            sport_name="Gymnastics",
            sport_id="1.gymnastics",
            output_dir="sport/output"
        )
        
        # 设置API相关配置
        self.api_url = 'https://www.gymnastics.sport/api/sportevents/'
        self.api_headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
            'dnt': '1',
            'referer': 'https://www.gymnastics.sport/site/events/search.php?type=sport',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # 更新HTTP客户端的头部
        self.http_client.session.headers.update(self.api_headers)
    
    def fetch_gymnastics_events(self) -> Dict[str, Any]:
        """获取体操比赛事件数据"""
        params = {
            'from': '2025-01-01',
            'to': '2025-12-31',
            'level': '',
            'discipline': '',
            'ageGroupType': '',
            'country': '',
            'title': '',
            'id': '',
            'status': ''
        }
        
        try:
            response = self.http_client.get(self.api_url, params=params)
            return response.json()
        except Exception as e:
            self.logger.error(f"获取体操比赛数据失败: {e}")
            return {}
    
    def process_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个比赛事件数据"""
        try:
            # 转换disciplines列表为逗号分隔的字符串
            disciplines = ', '.join([d['code'] for d in event.get('disciplines', [])])
            
            processed_event = {
                'ID': event.get('id', ''),
                'Title': event.get('title', ''),
                'Start Date': event.get('dateStart', ''),
                'End Date': event.get('dateEnd', ''),
                'Country': event.get('country', {}).get('name', ''),
                'Country Code': event.get('country', {}).get('code', ''),
                'City': event.get('city', ''),
                'Venue': event.get('venue', ''),
                'Level': event.get('level', {}).get('name', ''),
                'Level Code': event.get('level', {}).get('code', ''),
                'Disciplines': disciplines,
                'Age Group Type': event.get('ageGroupType', {}).get('name', ''),
                'Age Group Code': event.get('ageGroupType', {}).get('code', ''),
                'Status': event.get('status', {}).get('name', ''),
                'Status Code': event.get('status', {}).get('code', ''),
                'URL': f"https://www.gymnastics.sport/site/events/detail.php?id={event.get('id', '')}",
                'Created': event.get('created', ''),
                'Updated': event.get('updated', '')
            }
            
            return processed_event
            
        except Exception as e:
            self.logger.error(f"处理比赛事件数据失败: {e}")
            return {}
    
    def scrape(self) -> List[Dict[str, Any]]:
        """执行体操比赛数据爬取"""
        self.logger.info("开始获取体操比赛数据")
        
        # 获取原始数据
        raw_data = self.fetch_gymnastics_events()
        
        if not raw_data or 'data' not in raw_data:
            self.logger.error("未获取到有效的体操比赛数据")
            return []
        
        events = raw_data['data']
        processed_data = []
        
        self.logger.info(f"开始处理 {len(events)} 个比赛事件")
        
        for event in events:
            processed_event = self.process_event_data(event)
            if processed_event:
                processed_data.append(processed_event)
        
        self.logger.info(f"成功处理 {len(processed_data)} 个比赛事件")
        return processed_data


def main():
    """主函数"""
    scraper = GymnasticsScraper()
    
    try:
        data = scraper.run(save_format='xlsx')
        print(f"体操比赛数据爬取完成，共获取 {len(data)} 条数据")
        
    except Exception as e:
        print(f"爬虫运行失败: {e}")
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()