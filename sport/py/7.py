import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
import requests

url = "https://www.wbsc.org/en/calendar/2025"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

response.raise_for_status()  # 确保请求成功

from bs4 import BeautifulSoup
import requests


def parse_events(html):
    soup = BeautifulSoup(html, 'html.parser')
    events = []

    calendar_list = soup.find("div", class_="calendar-list")
    table = calendar_list.find("table")
    trs = table.find_all("tr")
    # 跳过表头并遍历
    for tr in trs[1:]:
        dates = tr.find_all('td', class_="date")
        start_date = dates[0].text
        end_date = dates[1].text if len(dates) > 1 else start_date
        event = {
            "month": tr.find('td', class_="month").text,
            "logo": tr.find('td', class_="logo").find("img")["src"],
            "name": tr.find('td', class_="name").text.strip(),
            "start_date": start_date,
            "end_date": end_date
        }

        # <tr style="cursor: pointer" class=" internal  " onclick="window.open('https://www.wbsc.org/en/events/2025-baseball-champions-league-americas/home','_self')">
        event["url"] = tr["onclick"].split("'")[1]

        # 打开url
        sub_response = requests.get(event["url"], headers=headers)

        sub_soup = BeautifulSoup(sub_response.text, 'html.parser')

        # <span class="hosts">Hosted by: </span>
        # <span class="flag-container">
        #                                                 <span class="flag-item"><span
        #                 class="flag-icon flag-icon-mx"></span>
        # MEX</span>
        #                                         </span>
        # 提取主办方
        hosts = sub_soup.find("span", class_="hosts")
        if hosts:
            event["hosts"] = hosts.next_sibling.next_sibling.text.strip()

        logging.info("Parsed event: %s", event)

        events.append(event)

    return events


# 示例用法
parsed_events = parse_events(response.text)

data = parsed_events

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