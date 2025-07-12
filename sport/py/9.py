import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


url = 'https://www.ihf.info/media-center/competitions/upcoming-events'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'priority': 'u=0, i',
    'referer': 'https://www.ihf.info/media-center/events/competitions',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

cookies = {
    '_ga': 'GA1.1.228513209.1739453533',
    'acceptCookies': '1',
    'cf_clearance': '6SAzzLdeFPx5QUP__oTi0IStfQAO9abQFEYjeeit5Fo-1740491307-1.2.1.1-OG79T0rzwu.d.9udvJgTwbky8MY8.Jf8SG8PSzu.mhuw7UQ5v5MrIxk6Q5ln0_kRPaMDhOtDM8wPE9AmO6P27DRS2s1EY2MhXJmktwyrDy2WkMVrci55YuknYvit_IRLE1Saz2wHEEQzWV56QSZT65DO3i0NiaScOobuwz8bE6WHsIs.OHKz36_N_uLT3NDSN9bQxcKwET9Rq_Yd5l81TUXa87RIvA7wUZAM3ViUNLWcwx.ZBt3Ymun1qS1K1WDZsZfJy4aJc6j4sM56kNyWfkg8O96cd3EE_2O1QRo7_Wc',
    '_ga_L2DC7J793W': 'GS1.1.1740491307.3.1.1740491478.0.0.0'
}

response = requests.get(url, headers=headers, cookies=cookies)

logging.info("Response status code: %s", response.status_code)
# logging.info("Response text: %s", response.text)

# 解析HTML内容
soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有符合条件的<h2>标签
h2_tags = soup.find_all('h2', {'data-toggle': 'tooltip', 'data-placement': 'top'})

titles = [tag.get('title') for tag in h2_tags]


# 查找所有具有 class "event-date" 的 span 元素
event_date_spans = soup.find_all('span', class_='event-date')

# 初始化一个空列表来存储日期对字典
date_pairs = []

# 遍历每个 span 元素，提取开始和结束时间
for span in event_date_spans:
    # 提取所有的 <time> 元素
    time_elements = span.find_all('time')

    # 确保有且只有两个 <time> 元素
    if len(time_elements) == 2:
        start_time_iso = time_elements[0]['datetime']  # ISO格式时间
        end_time_iso = time_elements[1]['datetime']  # ISO格式时间

        start_time_str = time_elements[0].get_text(strip=True)  # 显示的时间字符串
        end_time_str = time_elements[1].get_text(strip=True)  # 显示的时间字符串

        # 创建一个字典来存储这对日期
        date_pair = {
            'start_datetime_str': start_time_str,
            'end_datetime_str': end_time_str
        }

        # 将字典添加到列表中
        date_pairs.append(date_pair)

data = [{'title': title,
         'start_datetime_str': date_pair['start_datetime_str'],
         'end_datetime_str': date_pair['end_datetime_str']}
        for title, date_pair in zip(titles, date_pairs)]

print(data)


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