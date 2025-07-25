import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()

import requests
from bs4 import BeautifulSoup

url = "https://www.ijf.org/calendar?year=2025&month=&age=all&type=all"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

events = []
for row in soup.find_all("tr", attrs={"data-event-row-link": True}):
    event = {
        "date": row.find("td", {"data-t": "Date"}).get_text(strip=True),
        "icon_url": row.find("div", class_="event_ico")["style"].split("url(")[1].split(")")[0] if row.find("div", class_="event_ico") else None,
        "name": row.find("td", {"data-t": "Name"}).get_text(strip=True),
        "location": row.find("td", {"data-t": "Location"}).get_text(strip=True),
        "event_link": "https://www.ijf.org" + row.find("a", class_="event-link-title")["href"] if row.find("a", class_="event-link-title") else None,
    }
    events.append(event)

print(events)

data = events


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