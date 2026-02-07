import logging
import os

import pandas as pd
import requests

from util.log import setup_logging

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
    response = requests.get("https://www.uci.org/api/calendar/upcoming")
    logging.info(f"Request to {response.url} returned status code {response.status_code}")
    logging.info(f"Response content: {response.text}")

    data = response.json()

    # logging.info(f"Data: {data}")

    # {items: [{'month':2, 'year':2022}]
    items = data['items']
    flattened_data = []
    # 只保留year为2026的item
    for item_for_one_month in items:
        if item_for_one_month['year'] != 2026:
            continue
        logging.info(f"Item: {item_for_one_month}")

        # 再去获取items
        for item_for_one_day in item_for_one_month['items']:
            logging.info(f"Item: {item_for_one_day}")

            for item_for_one_competition in item_for_one_day['items']:
                logging.info(f"Item: {item_for_one_competition}")
                flatten_item = flatten_dict(item_for_one_competition)
                flattened_data.append(flatten_item)

    logging.info(f"去重之前的数据条数：{len(flattened_data)}")
    # flattened_data是列表，其中是一个个字典，其中可能包含key和value都完全相同的字典，请去重
    flattened_data = [dict(t) for t in {tuple(d.items()) for d in flattened_data}]

    logging.info(f"去重之后的数据条数：{len(flattened_data)}", )

    # logging.info(f"Flattened data: {flattened_data}")

    # Save to Excel
    save_to_excel(flattened_data, get_excel_name())

    logging.info("BWF tournament data processing completed successfully")