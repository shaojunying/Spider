# config.py

# 小区配置（可以支持多个小区）
communities = [
    {
        "name": "前进花园石门苑",
        "comm_id": "176561"
    },
    # {
    #     "name": "石景苑",
    #     "comm_id": "147478"
    # },
    # {
    #     "name": "前进花园牡丹苑",
    #     "comm_id": "376901"
    # },
    # {
    #     "name": "前进花园玉兰苑",
    #     "comm_id": "124987"
    # },
    # {
    #     "name": "前进花园一区",
    #     "comm_id": "51780"
    # },
    # {
    #     "name": "西辛南区",
    #     "comm_id": "167486"
    # },
    # {
    #     "name": "西辛北区",
    #     "comm_id": "83574"
    # }
]

# 要分析的小区名称，只能传递一个。如果为None，则分析所有小区
COMMUNITY_NAME = "前进花园石门苑"

import os

OUTPUT_PATH = './output'  # 输出目录

# 默认文件路径配置
DEFAULT_HISTORY_PATH = os.path.join(OUTPUT_PATH, 'price_history.csv')
DEFAULT_INFO_PATH = os.path.join(OUTPUT_PATH, 'houses_info.csv')