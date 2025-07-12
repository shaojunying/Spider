import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.fil-luge.org/en/results/results?event_season_id=32&event_category_id=0&event_type_id=0&event_date_from=&event_date_to="
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}
response = requests.get(url, headers=headers)
response.raise_for_status()  # 确保请求成功

html = response.text

from bs4 import BeautifulSoup


soup = BeautifulSoup(html, 'html.parser')
event_data = []

for category_div in soup.find_all("div", class_="col-xs-12 events"):
    category = category_div.find("h2").text.strip() if category_div.find("h2") else "Unknown"

    for event in category_div.find_all("div", class_="event-row"):
        link_tag = event.find("a", class_="event-link")

        date = link_tag.find("div", class_="col-xs-12 col-sm-3").text.strip() if link_tag.find("div",
                                                                                               class_="col-xs-12 col-sm-3") else ""
        title = link_tag.find("div", class_="event-title").text.strip() if link_tag.find("div",
                                                                                         class_="event-title") else ""
        country_flag = link_tag.find("img", class_="flag-icon")
        country = country_flag["src"] if country_flag else ""
        track_type = link_tag.find("div", class_="col-xs-12 col-sm-2").text.strip() if link_tag.find("div",
                                                                                                     class_="col-xs-12 col-sm-2") else ""
        url = link_tag["href"] if link_tag else ""

        event_data.append({
            "category": category,
            "date": date,
            "title": title,
            "country_flag": country,
            "track_type": track_type,
            "url": url
        })

data = event_data

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