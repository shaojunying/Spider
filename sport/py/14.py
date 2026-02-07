import logging
import os
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd

from util.log import setup_logging

setup_logging()


def parse_year(year : int) -> list[dict]:
    flattened_data = []
    for month in range(1, 13):
        logging.info(f"Parsing {year}-{month}")
        data = parse_month(year, month)
        flattened_data.extend(data)
    return flattened_data


def parse_month(year, month):
    # 获取HTML内容
    url = f"https://www.worlddancesport.org/Calendar/Competitions?Month={month}&Year={year}"
    response = requests.get(url)
    html_content = response.text
    logging.info(f"Request to {url} returned status code {response.status_code}")
    logging.debug("HTML content: \n" + html_content)
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到所有的<li>项
    items = soup.find_all('li', class_='calendarlist__itemwrapper')
    # 解析每个<li>项并存储为字典列表
    data = []
    for item in items:
        event = {}
        link = item.find('a', class_='calendarlist__item')
        event['url'] = link['href']

        date_p = item.find('p', class_='calendarlist__item__date')
        event['date'] = date_p.text.strip()

        location_p = item.find('p', class_='calendarlist__item__location')
        event['location'] = location_p.text.strip()

        competitions_p = item.find('p', class_='calendarlist__item__competitions')
        competitions_text = competitions_p.text.strip()

        # 将 \n 替换为 Excel 的换行符 \r\n
        competitions_text = competitions_text.replace('\n', '\r\n')

        event['competitions'] = competitions_text
        data.append(event)
    return data

flattened_data = parse_year(2026)

logging.info(f"Flattened data: {flattened_data}")


def save_to_excel(data: List[Dict], excel_path: str) -> None:
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
save_to_excel(flattened_data, get_excel_name())

logging.info("BWF tournament data processing completed successfully")