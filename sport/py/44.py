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

url = "https://www.ittf.com/2025-events-calendar/"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5",
    "dnt": "1",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-arch": "arm",
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-full-version": "133.0.6943.127",
    "sec-ch-ua-full-version-list": '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.127", "Chromium";v="133.0.6943.127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": "macOS",
    "sec-ch-ua-platform-version": "15.3.1",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}
cookies = {
    "language_redirect": "1",
    "_ga": "GA1.2.650042999.1742193850",
    "_gid": "GA1.2.1999143976.1742193850",
    "_gat": "1",
    "_gat_UA-81820650-1": "1",
    "cf_clearance": "zeOsBD0AcV4a1uT2dnByhhlaQsOvXFtXKxJY.29tby4-1742193871-1.2.1.1-asi2ISBpiEDqA2RY_PSm7KAx3P6pcmA6E9spvvXZAb0tpo4Uajn8qJRgT1kAgXLr4Lshpjd_5kxCDFli5wjmRmqQxywf8lv2EdCyh5mJjI7rO6_ifq1ZHseSm2bn3M54GjSBNPZs3rbS7yqlj1N.AtXLdQhRcK9wUtEpVH3FATvna4E7QlXWxwmisE_UPcGmsATyd0I7tDz76LihPRdeEv6urCVbsHDTKGulvMKJaUhbjaOSqabKrNyuRRvbsuDr8UPNE3fXhSAYDplCTS7_WyQiXQfSgi3FSpWzl5IDlvGbH6naGrKKeedg8u5.roavrGUMybvhxoko6dhS_DyshrNp5dkdOLh9FUeJEmynqSs9IVqmhweFd7UbxlM7JKRV08DP_A7mrnae8XZKZIFWe2HdBcFrua5kE1KwuhS7fPU",
    "_ga_C5E6Y3BPDF": "GS1.2.1742193850.1.1.1742193877.0.0.0",
    "_ga_FNXVH4KHWT": "GS1.2.1742193850.1.1.1742193877.0.0.0"
}

response = requests.get(url, headers=headers, cookies=cookies)

response.raise_for_status()  # 确保请求成功

from bs4 import BeautifulSoup


def parse_event_links(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    event_list = []

    div = soup.find("div", class_="content page-content")

    # 先获取到这样的结构 <p> <strong>Notes:</strong> </p> 只看格式，其中的内容不固定
    for p in div.find_all("p"):
        p_title = p.text.strip()
        if p_title == "Notes:" or p_title.strip() == '':
            continue

        # 找到它下一个ul标签
        ul = p.find_next("ul")

        for a_tag in ul.find_all('a', href=True):
            event = {
                "month": p_title,
                "name": a_tag.text.strip(),
                "url": a_tag['href']
            }
            event_list.append(event)

    return event_list


data = parse_event_links(response.text)



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