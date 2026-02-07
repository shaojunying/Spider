import json
import os
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

for month in range(1, 13):
    curl_command = f"""
    curl 'https://m.worldtaekwondo.org/calendar/cld_list.html?cym=2026-{month}&cldgn=' \
      `-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
      -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
      -H 'Connection: keep-alive' \
      -b '_ga=GA1.1.168236739.1742396930; _ga_5FTK8WS2DC=GS1.1.1742396929.1.1.1742396953.0.0.0; _ga_SPK6K870R3=GS1.1.1742396956.1.0.1742396956.0.0.0' \
      -H 'DNT: 1' \
      -H 'Referer: https://m.worldtaekwondo.org/calendar/cld_list.html?cym=2026-{month}&cldgn=' \
      -H 'Sec-Fetch-Dest: document' \
      -H 'Sec-Fetch-Mode: navigate' \
      -H 'Sec-Fetch-Site: same-origin' \
      -H 'Sec-Fetch-User: ?1' \
      -H 'Upgrade-Insecure-Requests: 1' \
      -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' \
      -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: "macOS"'`
    """

    result = subprocess.run(
        curl_command,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    soup = BeautifulSoup(result.stdout, 'html.parser')
    ul_elem = soup.find("ul", class_="date_day")
    for elem in ul_elem.find_all("li"):
        # 		<a href="cld_view.html?nid=142000&cym=2026-3&cldgn=">
# 				<span class="day">1 ~ 7</span>
# 				<span class="title" style="text-transform:none;">[KYORUGI] WT Online Kyorugi Coach Certification Course (LV1)</span>
# 				</a>
        a_elem = elem.find("a")
        title = a_elem.find("span", class_="title").text
        date = a_elem.find("span", class_="day").text
        href = a_elem.get("href")
        all_data.append({
            "title": title,
            "month": month,
            "date": date,
            "href": href
        })
    logging.info(f"Found {len(all_data)} entries")


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