import os

import requests


from util.log import setup_logging
import logging

setup_logging()

url = 'https://www.fie.org/competitions/search'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'DNT': '1',
    'Origin': 'https://www.fie.org',
    'Referer': 'https://www.fie.org/competitions',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

cookies = {
    'locale': 'en',
    '_gid': 'GA1.2.274794424.1740489014',
    '_gat_gtag_UA_57188458_1': '1',
    '_ga_0941VF31P4': 'GS1.1.1740489014.1.1.1740489254.0.0.0',
    '_ga': 'GA1.1.1870770868.1740489014',
    'connect.sid': 's%3AkDUzS26yUZVvRD2AY4xn3guzZWYckitM.bbfbplFjWfhvN4Z892B3WnWm4hu%2Bt%2FTAwol2uHzPdJk'
}

data = {
    'name': '',
    'status': '',
    'gender': [],
    'weapon': [],
    'type': [],
    'season': '-1',
    'level': '',
    'competitionCategory': '',
    'fromDate': '2025-01-01',
    'toDate': '2025-12-31',
    'fetchPage': 1
}

response = requests.post(url, headers=headers, cookies=cookies, json=data)

logging.info("Response status code: %s", response.status_code)
logging.info("Response text: %s", response.text)

data = response.json()

items = data['items']


def save_to_excel(data: list[dict], excel_path: str) -> None:
    """
    Save the tournament data to an Excel file
    """
    import pandas as pd
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
save_to_excel(items, get_excel_name())