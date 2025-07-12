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

url = "https://uww.org/apiv4/eventlisting?start_date=2025-01-01&end_date=2025-12-31"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

response.raise_for_status()  # 确保请求成功

data = json.loads(response.text)

result = []

for item in data['content']['items']:
    new_item = {}
    # title
    new_item['title'] = item.get('title', '')
    # city
    new_item['city'] = item.get('city', '')
    # event_end_date
    new_item['event_end_date'] = item.get('event_end_date', '')
    # event_start_date
    new_item['event_start_date'] = item.get('event_start_date', '')
    # field_age
    new_item['field_age'] = item.get('field_age', '')
    # field_country
    new_item['field_country'] = item.get('field_country', '')
    # field_country_noc
    new_item['field_country_noc'] = item.get('field_country_noc', '')
    # field_event_type
    new_item['field_event_type'] = item.get('field_event_type', '')
    # field_program
    new_item['field_program'] = item.get('field_program', '')
    # field_results
    new_item['field_results'] = item.get('field_results', '')
    # field_sport
    new_item['field_sport'] = item.get('field_sport', '')

    result.append(new_item)

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