import json
import os
import re
import subprocess

import pandas as pd
import requests
import logging

from bs4 import BeautifulSoup

from util.log import setup_logging

setup_logging()

import json
import subprocess

from bs4 import BeautifulSoup

all_data = []

for _ in range(1, 2):
    curl_command = f"""
    curl 'https://www.iwuf.org/apixh/index.php/Gjwl/get_calendar?callback=callback' \
  -H 'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01' \
  -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -b '_ga=GA1.1.598547600.1742199673; Hm_lvt_ee4f53865d5ceaa703d3a09b14df8f23=1742199674; HMACCOUNT=6B3580ACB8F3D8CA; Hm_lpvt_ee4f53865d5ceaa703d3a09b14df8f23=1742397569; _ga_GV3D6WT6XW=GS1.1.1742397569.2.0.1742397572.0.0.0; _ga_ZSXGQMFTZW=GS1.1.1742397569.2.0.1742397572.0.0.0' \
  -H 'DNT: 1' \
  -H 'Origin: https://www.iwuf.org' \
  -H 'Referer: https://www.iwuf.org/calendar/index.html' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw 'language=cn&year=2025&size=100&page=1'
    """

    result = subprocess.run(
        curl_command,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 1. 使用正则表达式提取 JSON 部分
    json_str = re.sub(r'^callback\((.*)\)$', r'\1', result.stdout)

    # 2. 解析 JSON 数据
    data = json.loads(json_str)

    # 3. 获取 "val" 里面的数据
    events = data["val"]

    # 4. 遍历所有月份的活动
    for month, events_list in events.items():
        print(f"📅 {month} 的活动:")
        for event in events_list:
            all_data.append({
                "title": event["title"],
                "date": event["date"],
                "city": event["city"],
                "organizer": event["organizer"]
            })


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