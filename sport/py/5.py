import os
import requests
import logging
import openpyxl
from sport import config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data(page: int, limit: int = 50):
    """获取指定页的数据"""
    url = 'https://graphql-prod-4707.prod.aws.worldathletics.org/graphql'
    headers = {
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://worldathletics.org',
        'Referer': 'https://worldathletics.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json',
        'x-amz-user-agent': 'aws-amplify/3.0.2',
        'x-api-key': 'da2-fxf3r4jszngxjgwhjfkpfvd4li',
    }
    data = {
        'operationName': 'getCalendarEvents',
        'variables': {
            'startDate': '2025-01-01',
            'endDate': '2025-12-31',
            'query': None,
            'regionType': 'world',
            'regionId': None,
            'disciplineId': None,
            'rankingCategoryId': None,
            'permitLevelId': None,
            'competitionGroupId': None,
            'competitionSubgroupId': 0,
            'limit': limit,
            'offset': page * limit,
            'showOptionsWithNoHits': None,
            'hideCompetitionsWithNoResults': False,
            'orderDirection': 'Ascending',
        },
        'query': '''query getCalendarEvents($startDate: String, $endDate: String, $query: String, $regionType: String, $regionId: Int, $currentSeason: Boolean, $disciplineId: Int, $rankingCategoryId: Int, $permitLevelId: Int, $competitionGroupId: Int, $competitionSubgroupId: Int, $competitionGroupSlug: String, $limit: Int, $offset: Int, $showOptionsWithNoHits: Boolean, $hideCompetitionsWithNoResults: Boolean, $orderDirection: OrderDirectionEnum) {
          getCalendarEvents(startDate: $startDate, endDate: $endDate, query: $query, regionType: $regionType, regionId: $regionId, currentSeason: $currentSeason, disciplineId: $disciplineId, rankingCategoryId: $rankingCategoryId, permitLevelId: $permitLevelId, competitionGroupId: $competitionGroupId, competitionSubgroupId: $competitionSubgroupId, competitionGroupSlug: $competitionGroupSlug, limit: $limit, offset: $offset, showOptionsWithNoHits: $showOptionsWithNoHits, hideCompetitionsWithNoResults: $hideCompetitionsWithNoResults, orderDirection: $orderDirection) {
            results {
              id
              name
              venue
              area
              rankingCategory
              disciplines
              competitionGroup
              competitionSubgroup
              startDate
              endDate
              dateRange
            }
          }
        }'''
    }

    try:
        logger.info(f"Fetching data for page {page}...")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data for page {page}: {e}")
        return None

def save_to_excel(results):
    """将结果保存到Excel文件"""
    logger.info("Saving data to Excel...")

    # 获取当前文件名并生成新的Excel文件名
    filename = os.path.basename(__file__)
    basename = os.path.splitext(filename)[0]
    new_filename = basename + ".xlsx"
    excel_file_path = os.path.join(config.output_path, new_filename)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        'ID', 'Name', 'Venue', 'Area', 'Ranking Category', 'Disciplines',
        'Competition Group', 'Competition Subgroup', 'Start Date', 'End Date', 'Date Range'
    ])

    for result in results:
        ws.append([
            result.get('id'),
            result.get('name'),
            result.get('venue'),
            result.get('area'),
            result.get('rankingCategory'),
            result.get('disciplines'),
            result.get('competitionGroup'),
            result.get('competitionSubgroup'),
            result.get('startDate'),
            result.get('endDate'),
            result.get('dateRange'),
        ])

    wb.save(excel_file_path)
    logger.info(f"Data saved to {excel_file_path}")

def main():
    # 获取分页数据并保存
    all_results = []
    page = 0
    limit = 50

    while True:
        data = fetch_data(page, limit)
        if not data or not data.get('data') or not data['data'].get('getCalendarEvents') or not data['data']['getCalendarEvents'].get('results'):
            logger.info("No more data to fetch.")
            break

        results = data['data']['getCalendarEvents']['results']
        all_results.extend(results)

        # 检查是否还有更多分页数据
        if len(results) < limit:
            break

        page += 1

    if all_results:
        save_to_excel(all_results)
    else:
        logger.warning("No results found.")

if __name__ == '__main__':
    main()