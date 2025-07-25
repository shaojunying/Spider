import os
import requests
import pandas as pd
import logging
from sport import config

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# 请求API获取比赛数据
def fetch_competitions(page):
    url = f"https://api.worldaquatics.com/fina/competitions?pageSize=100&venueDateFrom=2025-01-01T00%3A00%3A00%2B00%3A00&venueDateTo=2026-01-01T00%3A00%3A00%2B00%3A00&disciplines=&group=FINA&sort=dateFrom%2Casc&page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 抛出HTTP错误
        logger.info(f"Successfully fetched data for page {page}.")
        return response.json()  # 解析JSON数据并返回
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data for page {page}: {e}")
        return None


# 处理API数据并保存为Excel
def process_and_save_data():
    page = 0
    all_data = []

    # 循环获取所有页面的数据
    while True:
        logger.info(f"Fetching data for page {page}...")
        data = fetch_competitions(page)

        if not data or 'content' not in data:
            logger.warning(f"No data found on page {page}, or API response format changed.")
            break

        all_data.extend(data['content'])

        if page + 1 >= data['pageInfo']['numPages']:
            logger.info("All pages fetched.")
            break

        page += 1

    # 处理数据并保存到DataFrame
    if all_data:
        logger.info("Processing data into DataFrame...")
        competitions = []
        for item in all_data:
            competition = {
                "id": item.get("id"),
                "name": item.get("name"),
                "officialName": item.get("officialName"),
                "dateFrom": item.get("dateFrom"),
                "dateTo": item.get("dateTo"),
                "venueDateFrom": item.get("venueDateFrom"),
                "venueDateTo": item.get("venueDateTo"),
                "country": item['location'].get("countryName"),
                "city": item['location'].get("city"),
                "competitionType": item['competitionType'].get("name"),
                "disciplines": ", ".join(item['disciplines'])
            }
            competitions.append(competition)

        # 将数据转换为DataFrame
        df = pd.DataFrame(competitions)

        # 设置文件名
        filename = os.path.basename(__file__)
        basename = os.path.splitext(filename)[0]
        new_filename = basename + ".xlsx"
        excel_file_path = os.path.join(config.output_path, new_filename)

        # 保存为Excel文件
        try:
            logger.info(f"Saving data to Excel file: {excel_file_path}")
            df.to_excel(excel_file_path, index=False)
            logger.info("Data saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save data to Excel: {e}")


if __name__ == "__main__":
    process_and_save_data()