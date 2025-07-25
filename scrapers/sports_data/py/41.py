import json

import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.ifsc-climbing.org/api/dapi/events/all?dateFrom=$range(2025-01-01,2025-12-31)&limit=100"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

# 解析JSON数据
data = json.loads(response.text)

# 构造字典数组
result = []
for item in data['items']:
    new_item = dict()
    fields = item.get('fields', {})
    new_item['dateFrom'] = fields.get('dateFrom', '')
    new_item['dateTo'] = fields.get('dateTo', '')
    new_item['description'] = fields.get('description', '')
    new_item['headline'] = fields.get('headline', '')
    new_item['location'] = fields.get('location', '')
    new_item['venue'] = fields.get('venue', '')
    new_item['url'] = item.get('url', '')

    result.append(new_item)

# 按照dateFrom排序
result = sorted(result, key=lambda x: x['dateFrom'])

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