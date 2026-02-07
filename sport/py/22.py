import requests
from datetime import datetime

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


# 定义API的URL
url = 'https://api.isu-skating.com/api/event/list'

# 定义请求头
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-store',
    'Connection': 'keep-alive',
    'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryzDGGtTYfrIvmsZGO',
    'DNT': '1',
    'Origin': 'https://isu-skating.com',
    'Referer': 'https://isu-skating.com/events/?month=February&season=2024%2F2026',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

# 定义请求体模板
body_template = (
    '------WebKitFormBoundaryzDGGtTYfrIvmsZGO\r\n'
    'Content-Disposition: form-data; name="pagesize"\r\n\r\n2000\r\n'
    '------WebKitFormBoundaryzDGGtTYfrIvmsZGO\r\n'
    'Content-Disposition: form-data; name="month_name"\r\n\r\n{month}\r\n'
    '------WebKitFormBoundaryzDGGtTYfrIvmsZGO\r\n'
    'Content-Disposition: form-data; name="season"\r\n\r\n{season}\r\n'
    '------WebKitFormBoundaryzDGGtTYfrIvmsZGO--\r\n'
)

# 获取当前年份
current_year = datetime.now().year

# 定义月份列表
months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

all_data = []

# 循环枚举每个月份
for month in months:
    # 构建请求体
    body = body_template.format(month=month, season=f'{current_year-1}/{current_year}')

    # 发送POST请求
    response = requests.post(url, headers=headers, data=body)

    # 打印请求状态码
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response text: %s", response.text)

    data = response.json()
    data = data['data']
    for item in data:
        flatten_data = flatten_dict(item)
        all_data.append(flatten_data)


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
save_to_excel(all_data, get_excel_name())