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

page = 1
for page in range(1, 5):
    curl_command = f"""
    curl 'https://www.theuiaa.org/wp-json/tribe/views/v2/html' \
      -H 'accept: */*' \
      -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
      -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' \
      -b 'cmplz_consented_services=; cmplz_policy_id=16; cmplz_marketing=allow; cmplz_statistics=allow; cmplz_preferences=allow; cmplz_functional=allow; cmplz_banner-status=dismissed; _ga=GA1.1.1975670860.1742191527; _ga_GD495V2FJ2=GS1.1.1742394965.2.1.1742396011.0.0.0; _ga_5D943P24PY=GS1.1.1742394965.2.1.1742396012.0.0.0' \
      -H 'dnt: 1' \
      -H 'origin: https://www.theuiaa.org' \
      -H 'priority: u=1, i' \
      -H 'referer: https://www.theuiaa.org/uiaa-calendar/' \
      -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: "macOS"' \
      -H 'sec-fetch-dest: empty' \
      -H 'sec-fetch-mode: cors' \
      -H 'sec-fetch-site: same-origin' \
      -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' \
      -H 'x-requested-with: XMLHttpRequest' \
      --data-raw 'prev_url=https%3A%2F%2Fwww.theuiaa.org%2Fcalendar%2Flist%2F%3Fpagename%3Duiaa-calendar%26shortcode%3D24f53d40%26eventDisplay%3Dpast&url=https%3A%2F%2Fwww.theuiaa.org%2Fcalendar%2Flist%2Fpage%2F{page}%2F%3Fshortcode%3D24f53d40&should_manage_url=false&shortcode=24f53d40&_tec_view_rest_nonce_primary=f67093d5f5&_tec_view_rest_nonce_secondary='
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
    json_data = soup.find("script", {"type": "application/ld+json"})
    if json_data is None:
        break

    data = json.loads(json_data.text)

    for item in data:
        new_item = {}
        new_item['name'] = item.get('name')
        new_item['image'] = item.get('image')
        new_item['url'] = item.get('url')
        new_item['eventStatus'] = item.get('eventStatus')
        new_item['startDate'] = item.get('startDate')
        new_item['endDate'] = item.get('endDate')
        new_item['performer'] = item.get('performer')

        all_data.append(new_item)


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