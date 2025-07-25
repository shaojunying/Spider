import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.ibsf.org/en/races-and-results?tx_fmresults_list%5B__referrer%5D%5B%40extension%5D=FmResults&tx_fmresults_list%5B__referrer%5D%5B%40controller%5D=List&tx_fmresults_list%5B__referrer%5D%5B%40action%5D=main&tx_fmresults_list%5B__referrer%5D%5Barguments%5D=YTo1OntzOjg6ImV2ZW50X2lkIjtzOjA6IiI7czo5OiJzZWFzb25faWQiO3M6NzoiMTAwMDAwNCI7czoxNjoic2Vzc2lvbl90eXBlX2lkcyI7czowOiIiO3M6NToic3BvcnQiO3M6MDoiIjtzOjk6InRyYWluaW5ncyI7czowOiIiO30%3D7e3ec79ba2042954aac3fe3f8ef5d50f99ff8627&tx_fmresults_list%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22FmResults%22%2C%22%40controller%22%3A%22List%22%2C%22%40action%22%3A%22main%22%7D2f4e45e169d2363ac0f69e19bf11567a60cdc86d&tx_fmresults_list%5B__trustedProperties%5D=%7B%22sport%22%3A1%2C%22season_id%22%3A1%2C%22session_type_ids%22%3A1%2C%22event_id%22%3A1%2C%22trainings%22%3A1%7Dc7a3c325f8425ead471e0c6286b082a9f6d6f280&tx_fmresults_list%5Bsport%5D=&tx_fmresults_list%5Bseason_id%5D&tx_fmresults_list%5Bsession_type_ids%5D=&tx_fmresults_list%5Bevent_id%5D=&tx_fmresults_list%5Btrainings%5D="
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

# 解析HTML内容
soup = BeautifulSoup(response.text, 'html.parser')

# 初始化一个空列表来保存比赛信息
competitions = []

# 查找所有的比赛行
for tr in soup.find_all('tr'):
    if not tr.has_attr('data-competition-id'):
        continue
    competition = {'id': tr.get('data-competition-id')}

    # 提取比赛ID

    # 提取比赛日期
    date_cell = tr.find('td', class_='resultBlock__col--competition-date')
    date_span = date_cell.find('span', attrs={'data-datelocal': True})
    competition['date'] = date_span['data-datelocal']

    # 提取比赛类型
    session_type_cell = tr.find('td', class_='resultBlock__col--competition-sessiontype')
    competition['session_type'] = session_type_cell.get_text(strip=True)

    # 提取比赛名称
    name_cell = tr.find('td', class_='text-center').find('div', class_='text-small text-nowrap')
    competition['name'] = name_cell.get_text(strip=True)

    # 提取比赛地点
    location_cell = tr.find('td', class_='text-nowrap text-center').find_all('div', class_='text-small text-nowrap')[0]
    competition['location'] = location_cell.get_text(strip=True)

    # 将比赛信息添加到列表中
    competitions.append(competition)

data = competitions


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