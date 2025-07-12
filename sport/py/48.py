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

url = "https://iwf.sport/events/calendar/?cy=2025"
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

response.raise_for_status()  # 确保请求成功

from bs4 import BeautifulSoup
import requests


def parse_events(html):
    soup = BeautifulSoup(html, 'html.parser')
    events = []

    groups = soup.find_all("div", class_="group")
    for group in groups:
        title = group.find("h3").text.strip() if group.find("h3") else "Unknown"
        cards = group.find_all("a", class_="card")

        for card in cards:
            date_text = card.find("p", class_="location").text.strip()
            link = card["href"] if card.has_attr("href") else ""
            event_title = card.find("p", class_="title").text.strip() if card.find("p", class_="title") else "Unknown"
            event_type = card.find("span", class_="text").text.strip() if card.find("span",
                                                                                    class_="text") else "Unknown"
            location = card.find_all("p", class_="location")[-1].text.strip()

            event = {
                "month": title,
                "title": event_title,
                "date": date_text,
                "link": link,
                "event_type": event_type,
                "location": location
            }
            events.append(event)

    return events


# 示例用法
parsed_events = parse_events(response.text)

data = parsed_events

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