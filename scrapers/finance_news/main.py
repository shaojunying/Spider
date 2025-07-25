import requests
import json
from datetime import datetime, timedelta

url_template = 'https://www.cls.cn/v1/roll/get_roll_list?app=CailianpressWeb&category=red&last_time={}&os=web&refresh_type=1&rn=20&sv=7.7.5&sign=1844fbb28877ce5ccc170c4f8f058179'
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'HWWAFSESID=50a817f0492394dcc7; HWWAFSESTIME=1705302373278; vipNotificationState=on; isMinimize=off; Hm_lvt_fa5455bb5e9f0f260c32a1d45603ba3e=1705302376; hasTelegraphNotification=off; hasTelegraphSound=off; hasTelegraphRemind=off; Hm_lpvt_fa5455bb5e9f0f260c32a1d45603ba3e=1705302412',
    'DNT': '1',
    'Referer': 'https://www.cls.cn/telegraph',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': 'Not_A Brand;v=8, Chromium;v=120, Google Chrome;v=120',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'macOS'
}

visited_ids = set()  # 用于存储已访问过的内容的id
desired_count = 600  # 期望获取的数据条数
current_count = 0  # 当前获取的数据条数

current_last_time = int(datetime.now().timestamp())  # 初始化为当前时间

while current_count < desired_count:
    response = requests.get(url_template.format(current_last_time), headers=headers)  # 使用当前时间戳获取内容
    data = response.json()

    if 'data' in data and 'roll_data' in data['data']:
        roll_data = data['data']['roll_data']
        for item in roll_data:
            article_id = item.get('id')
            if article_id not in visited_ids:
                title = item.get('title')
                content = item.get('content')
                ctime = item.get('ctime')
                current_last_time = min(current_last_time, ctime - 60)
                reading_num = item.get('reading_num')
                share_num = item.get('share_num')
                comment_num = item.get('comment_num') 

                print(f'Title: {title}')
                print(f'Content: {content}')
                print(f'Time: {datetime.fromtimestamp(ctime)}')
                print(f'Reading number: {reading_num}')
                print(f'Sharing number: {share_num}')
                print(f'Comment number: {comment_num}')
                
                print('\n')

                visited_ids.add(article_id)
                current_count += 1

            if current_count >= desired_count:
                break  # 达到目标数量后停止循环

# 如果没有达到目标数量，输出提示信息
if current_count < desired_count:
    print(f'Warning: Unable to retrieve {desired_count} items. Retrieved {current_count} items.')
