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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 配置无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小
chrome_options.add_argument("--no-sandbox")  # 解决某些环境下的问题
chrome_options.add_argument("--disable-dev-shm-usage")  # 解决某些系统共享内存不足问题
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# 启动 WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 访问 URL
url = "https://api.wtatennis.com/tennis/tournaments/?page=0&pageSize=100&excludeLevels=ITF&from=2026-01-01&to=2026-12-31"
driver.get(url)

# 获取页面返回的 JSON
response_text = driver.find_element("tag name", "body").text
# print(response_text)

# 关闭浏览器
driver.quit()
# curl_command = f"""
# curl -X GET "https://m.itftennis.com/tennis/api/TournamentApi/GetCalendar?circuitCode=WT&searchString=&skip=0&take=100&nationCodes=CHN&zoneCodes=&dateFrom=2026-01-01&dateTo=2026-12-31&indoorOutdoor=&categories=&isOrderAscending=true&orderField=startDate&surfaceCodes=" \
#  -H "Accept: application/json" \
#  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
# """

# result = subprocess.run(
#     curl_command,
#     shell=True,
#     check=True,
#     stdout=subprocess.PIPE,
#     stderr=subprocess.PIPE,
#     text=True
# )
# logging.info("result: " + result.stdout)
data = json.loads(response_text)

for item in data['content']:
    all_data.append({
        "tournamentGroup": item.get('tournamentGroup'),
        "title": item.get('title'),
        "startDate": item.get('startDate'),
        "endDate": item.get('endDate'),
        "surface": item.get('surface'),
        "inOutdoor": item.get('inOutdoor'),
        "city": item.get('city'),
        "country": item.get('country'),
        "prizeMoney": item.get('prizeMoney'),
        "prizeMoneyCurrency": item.get('prizeMoneyCurrency'),
        "liveScoringId": item.get('liveScoringId')
    })


logging.info(f"Found {len(all_data)} entries")


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