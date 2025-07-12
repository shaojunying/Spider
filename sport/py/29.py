import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.wkf.net/calendar"
headers = {
    "DNT": "1",
    "Referer": "https://www.wkf.net/calendar",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

# 解析HTML
soup = BeautifulSoup(response.text, "html.parser")

events = []
current_month = None  # 记录当前的月份

# 遍历HTML结构
for element in soup.find_all(["div", "tr"]):
    # 处理月份
    if element.name == "div" and "item-month" in element.get("class", []):
        month_tag = element.find("p")
        if month_tag:
            current_month = month_tag.text.strip()

    # 处理赛事数据行
    elif element.name == "tr":
        event_data = {}
        if current_month:
            event_data["month"] = current_month  # 添加月份信息

        serie_tag = element.find("td", {"data-title": "SERIE"})
        if serie_tag and serie_tag.find("img"):
            event_data["series"] = serie_tag.find("img").get("alt", "").strip()

        date_tag = element.find("td", {"data-title": "DATE"})
        if date_tag:
            event_data["date"] = date_tag.get_text(strip=True)

        event_tag = element.find("td", {"data-title": "EVENT"})
        if event_tag and event_tag.find("a"):
            event_data["event"] = event_tag.find("a").text.strip()

        if len(event_data) > 1:  # 确保 event_data 至少有2个字段
            events.append(event_data)

# 输出解析结果
import json
print(json.dumps(events, indent=2, ensure_ascii=False))


data = events


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