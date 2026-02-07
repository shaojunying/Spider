import os
from datetime import datetime

import pandas as pd
import requests

from util.log import setup_logging
import logging

setup_logging()



def flatten_dict(d, parent_key='', sep='_'):
    """
    展平嵌套的字典。

    :param d: 要展平的字典
    :param parent_key: 父键的前缀
    :param sep: 分隔符
    :return: 展平后的字典
    """
    items = {}
    for k, v in d.items():
        # 构建新的键名
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # 递归展平嵌套的字典
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


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

if __name__ == '__main__':

    url = 'https://world-rowing-api.soticcloud.net/stats/api/competition'
    params = {
        # 将下面字段转为datetime获取现在的时间
        'filter[StartDate]': f'{datetime.now().isoformat()}Z',
        'filter[competitionType.competitionCategory.DisplayName]': '',
        'filterOptions[StartDate]': 'greaterThanEqualTo',
        'include': 'competitionType.competitionCategory',
        'group': 'year'
    }

    response = requests.get(url, params=params)

    logging.info(f"Request to {response.url} returned status code {response.status_code}")
    logging.info(f"Response content: {response.text}")

    data = response.json()

    # 提取2026年的比赛列表
    competitions_2026_list = data['data']['2026']

    logging.info(f"2026 competitions: {competitions_2026_list}")

    flattened_data = []

    for competition in competitions_2026_list:
        logging.info(f"Competition: {competition}")
        # 展平比赛数据
        flattened_competition = flatten_dict(competition)

        flattened_data.append(flattened_competition)

    # Save to Excel
    save_to_excel(flattened_data, get_excel_name())

    logging.info("BWF tournament data processing completed successfully")



