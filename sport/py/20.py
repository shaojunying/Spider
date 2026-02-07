import json
import os
import subprocess

import pandas as pd
import requests
import logging

from bs4 import BeautifulSoup

from util.log import setup_logging

setup_logging()

import requests
page = 1

# 初始化字典列表
event_dicts = []

while True:
    curl_command = f"""
       curl 'https://www.fei.org/disciplines/ajax/events' \
      -H 'accept: */*' \
      -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
      -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' \
      -b 'SSESS6dc92097a694dfc33d4dfb0fdaa48611=YJtY7Pl7jG1Qy-50e_VRnFtihMfLuuXl8JtvHgH4LCU; _ga=GA1.1.1185993036.1740485737; _gcl_au=1.1.750753661.1740485742; fei_gdpr_2=allowed; _rdt_uuid=1740485737554.129d2009-fa0b-4922-ac31-7239dd75276e; _ga_0VEXYH3WXC=GS1.1.1742199833.4.1.1742199840.0.0.0; datadome=cE7K~ETduKw8eXm~F79ua4lkRh8VGYqO9Vf3860BiYrKcUCfQWrM4Cbbx16XD9yhQzvKKBnJsoq8Cb5lmF5hUH53Ru5rRCjEvDO8VzfUgJDMd9adBMWkmJtHGFFlW0pX; _ga_BP704Q3028=GS1.1.1742199833.4.1.1742199858.35.0.0' \
      -H 'dnt: 1' \
      -H 'origin: https://www.fei.org' \
      -H 'priority: u=1, i' \
      -H 'referer: https://www.fei.org/events?month=01&year=2026&country=CHN' \
      -H 'sec-ch-device-memory: 8' \
      -H 'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"' \
      -H 'sec-ch-ua-arch: "arm"' \
      -H 'sec-ch-ua-full-version-list: "Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.127", "Chromium";v="133.0.6943.127"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-model: ""' \
      -H 'sec-ch-ua-platform: "macOS"' \
      -H 'sec-fetch-dest: empty' \
      -H 'sec-fetch-mode: cors' \
      -H 'sec-fetch-site: same-origin' \
      -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36' \
      -H 'x-requested-with: XMLHttpRequest' \
      --data-raw 'month=all&search=&page={page}&year=2026&country=CHN&csrfToken=Mjk1NTg0NTY0NjdkN2RjZGM5ODk4OTUuNzE0MTgwOTg%253D'
       """


    result = subprocess.run(
        curl_command,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    data = json.loads(result.stdout)

    html = data['results']

    # print(html)
    logging.info('Page: %s', page)

    # 解析HTML响应
    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有包含事件信息的div元素
    event_divs = soup.find_all('div', class_='event-request-result')

    if event_divs is None or len(event_divs) == 0:
        break


    # 遍历每个div元素，提取所需信息并构建字典
    for div in event_divs:
        event_dict = {}
        event_dict['show_name'] = div.find('div', class_='show-name').text.strip()

        # 提取 show_disciplines 并转换为逗号分隔的字符串
        show_disciplines = div.find('div', class_='show-disciplines')
        if show_disciplines:
            event_dict['show_disciplines'] = ", ".join(span.text.strip() for span in show_disciplines.find_all('span'))
        else:
            event_dict['show_disciplines'] = ""  # 或者赋值 None

        event_dict['show_country'] = div.find('div', class_='show-country').find('span',
                                                                                 class_='flag-icon-cn').next_sibling.strip()
        event_dict['show_events'] = div.find('div', class_='show-events').text.strip()

        # 解析日期
        show_dates_div = div.find('div', class_='show-dates')
        if show_dates_div:
            days = show_dates_div.find('div', class_='days').text.strip()
            months = [span.text.strip() for span in show_dates_div.find('div', class_='months').find_all('span')]

            # 处理日期格式
            if months[0] == months[1]:  # 相同月份
                formatted_date = f"{months[0]} {days.replace(' - ', '-')}"
            else:  # 跨月份
                start_day, end_day = days.split(' - ')
                formatted_date = f"{months[0]} {start_day}-{months[1]} {end_day}"

            event_dict['show_dates'] = formatted_date
        else:
            event_dict['show_dates'] = None  # 处理缺失日期的情况

        event_dicts.append(event_dict)
    page += 1
# 打印字典列表
print(event_dicts)

all_data = event_dicts



def save_to_excel(data: list[dict], excel_path: str) -> None:
    """
    Save the tournament data to an Excel file
    """
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
    filename = os.path.basename(__file__)
    basename = os.path.splitext(filename)[0]
    new_filename = basename + ".xlsx"
    from sport import config
    excel_file_path = os.path.join(config.output_path, new_filename)
    logging.info(f"Saving excel file: {excel_file_path}")
    return str(excel_file_path)


# Save to Excel
save_to_excel(all_data, get_excel_name())