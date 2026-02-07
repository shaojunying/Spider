import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.worldsquash.org/wsf-calendar/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

from bs4 import BeautifulSoup

html = response.text

soup = BeautifulSoup(html, "html.parser")

# 找到2026年的部分
matches = []
for h2 in soup.find_all("h2"):
    a = h2.find("a", id = "Date2026")
    if a is None:
        continue
    table = h2.find_next("table")  # 找到紧随其后的表格
    for row in table.find_all("tr")[1:]:  # 跳过表头
        cols = row.find_all("td")
        if len(cols) >= 6:
            match = {
                "date": cols[0].text.strip(),
                "event": cols[1].text.strip(),
                "men": cols[2].text.strip(),
                "women": cols[3].text.strip(),
                "location": cols[4].text.strip(),
                "country": cols[5].text.strip(),
            }
            if match['event'] is None or match['event'].strip() == "":
                continue
            matches.append(match)

    print(matches)

data = matches


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