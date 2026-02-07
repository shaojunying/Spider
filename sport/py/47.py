import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

import requests

page = 0

result = []

while True:
    url = "https://gavnabd4cq-dsn.algolia.net/1/indexes/tri_prod_events_reverse/query"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "DNT": "1",
        "Origin": "https://triathlon.org",
        "Referer": "https://triathlon.org/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "X-Algolia-API-Key": "65d0db53c03e515dbedbc8ecb4c4cd45",
        "X-Algolia-Application-Id": "GAVNABD4CQ",
        "sec-ch-ua": "Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS"
    }
    data = {
        "query": "",
        "facets": "*",
        "filters": "(year:'2026')",
        "hitsPerPage": 15,
        "numericFilters": "finish_date_timestamp>1742195239",
        "page": page
    }
    response = requests.post(url, headers=headers, json=data)

    data = json.loads(response.text)

    for match in data['hits']:
        new_item = {}
        # name
        new_item['name'] = match.get('name', '')
        # start_date
        new_item['start_date'] = match.get('start_date', '')
        # finish_date
        new_item['finish_date'] = match.get('finish_date', '')
        # city
        new_item['city'] = match.get('city', '')
        # country_name
        new_item['country_name'] = match.get('country_name', '')
        # country_noc
        new_item['country_noc'] = match.get('country_noc', '')
        # event_categories，里面是个str列表，将其转为逗号分隔的字符串
        new_item['event_categories'] = ', '.join(match.get('event_categories', []))
        # venue
        new_item['venue'] = match.get('venue', '')
        # sport_categories
        new_item['sport_categories'] = ', '.join(match.get('sport_categories', []))
        result.append(new_item)
    logging.info("Page: %d, Total: %d", page, len(result))
    page += 1
    if page >= data['nbPages']:
        break

data = result


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