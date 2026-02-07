import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.worldskate.org/events/upcoming-events.html?filtri=1&mese=&anno=2026&category=&name="
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

from bs4 import BeautifulSoup

# 解析HTML内容
soup = BeautifulSoup(response.text, 'html.parser')

# 存储比赛信息的列表
events = []

# 获取所有比赛卡片
event_cards = soup.find_all('div', class_='eve_card')

for card in event_cards:
    event_info = {}

    # 提取比赛日期
    date_div = card.find('div', class_='data')
    if date_div:
        giorno = date_div.find('span', class_='giorno').text.strip()
        mese = date_div.find('span', class_='mese').text.strip()
        event_info['date'] = f"{giorno} {mese}"

    # 提取比赛标题
    title_h3 = card.find('h3')
    if title_h3:
        event_info['title'] = title_h3.text.strip()

    # 提取比赛地点
    location_p = card.find('p', class_='loc')
    if location_p:
        event_info['location'] = location_p.text.strip()

    # 提取比赛链接
    link_a = card.find('a', href=True)
    if link_a:
        event_info['link'] = link_a['href']

    # 将比赛信息添加到列表
    events.append(event_info)

data = events

# 打印所有提取到的比赛信息
for event in events:
    print(event)


def save_to_excel(data: list[dict], excel_path: str) -> None:
    """
    Save the tournament data to an Excel file
    """
    import pandas as pd
    import os
    try:
        df = pd.DataFrame(data)

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)

        # Save to Excel
        df.to_excel(excel_path, index=False, sheet_name='Tournaments')

        logging.info(f"Successfully saved data to Excel file: {excel_path}")
    except Exception as e:
        logging.error(f"Error saving to Excel: {str(e)}")
        raise

def get_excel_name() -> str:
    import os
    filename = os.path.basename(__file__)
    basename = os.path.splitext(filename)[0]
    new_filename = basename + ".xlsx"
    from sport import config
    excel_file_path = os.path.join(config.output_path, new_filename)
    logging.info(f"Saving excel file: {excel_file_path}")
    return str(excel_file_path)


# Save to Excel
save_to_excel(data, get_excel_name())