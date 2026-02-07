import requests
from bs4 import BeautifulSoup

from util.log import setup_logging
import logging

setup_logging()


import requests
from bs4 import BeautifulSoup

# 发送请求
url = "https://www.canoeicf.com/all-key-dates-icf-events-2026"

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

# # 处理带有 class="col-xs-12 events" 的 div 元素
# for category_div in soup.find_all("div", class_="col-xs-12 events"):
#     category = category_div.find("h2").text.strip() if category_div.find("h2") else "Unknown"
#
#     for event in category_div.find_all("div", class_="event-row"):
#         link_tag = event.find("a", class_="event-link")
#
#         date = ""
#         title = ""
#         country = ""
#         track_type = ""
#         url = ""
#
#         if link_tag:
#             date_tag = link_tag.find("div", class_="col-xs-12 col-sm-3")
#             date = date_tag.text.strip() if date_tag else ""
#
#             title_tag = link_tag.find("div", class_="event-title")
#             title = title_tag.text.strip() if title_tag else ""
#
#             country_flag = link_tag.find("img", class_="flag-icon")
#             country = country_flag["src"] if country_flag and "src" in country_flag.attrs else ""
#
#             track_tag = link_tag.find("div", class_="col-xs-12 col-sm-2")
#             track_type = track_tag.text.strip() if track_tag else ""
#
#             url = link_tag["href"] if "href" in link_tag.attrs else ""
#
#         event_data.append({
#             "category": category,
#             "date": date,
#             "title": title,
#             "country_flag": country,
#             "track_type": track_type,
#             "url": url
#         })

# 处理带有 class="ribbon-base" 的 div 元素
for month_div in soup.find_all("div", class_="ribbon-base"):
    month = month_div.find("p").text.strip() if month_div.find("p") else "Unknown"

    for event_li in month_div.find_next("ul").find_all("li"):
        title_tag = event_li.find("a", recursive=False)
        date_tag = event_li.find_all("a")[-1] if event_li.find_all("a") else None  # 确保至少有一个 <a> 标签

        title = ""
        location = ""
        date = ""
        url = ""

        if title_tag:
            title = title_tag.text.strip() if title_tag else ""
            # print(title_tag.next_sibling)
            # print(title_tag.next_sibling.next_sibling)
            # print(title_tag.next_sibling.next_sibling.text)
            location = title_tag.next_sibling.next_sibling.text if (title_tag
                                                                       and title_tag.next_sibling
                                                                       and title_tag.next_sibling.next_sibling
                                                                       )  else ""

        if date_tag:
            date = date_tag.text.strip() if date_tag else ""
            url = title_tag["href"] if "href" in title_tag.attrs else ""

        event_data.append({
            "month": month,
            "title": title,
            # "location": location,
            "date": date,
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