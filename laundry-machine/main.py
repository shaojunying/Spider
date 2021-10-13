import argparse
import json
import logging
import os
import pickle
import time

import requests

from config import *

# 获取验证码的链接
GET_VERIFY_CODE_URL = "https://u.zhinengxiyifang.cn/api/CheckCodes/getVerifyCode"
# 登录URL
LOGIN_URL = "https://u.zhinengxiyifang.cn/api/UcleanWechatUsers/loginByMobile"
# 创建订单
CREATE_ORDER_URL = "https://u.zhinengxiyifang.cn/api/UcleanWechatUsers/{open_id}/createOrder"
# 查询洗衣机剩余时间URL
REMAIN_TIME_URL = "https://u.zhinengxiyifang.cn/api/Stores/getStoreDetails"

headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Mobile/15E148 MicroMessenger/8.0.9(0x18000923) NetType/WIFI Language/zh_CN",
    "Referer": "https://wx.zhinengxiyifang.cn/index.html",
    "Accept-Language": "zh-cn"
}

# 使用session,每次请求会携带之前的cookies
s = requests.session()


class Notice:

    def send_message(self, title=None, body=None):
        data = {
            'title': title,
            'body': body
        }
        for url in SEND_NOTICE_URLS:
            response = requests.post(url, data=data)
            logging.debug("%s, %s".format(response.status_code, response.text))


def save_param_to_file(authorization, cookies, open_id):
    """
    保存cookie、header到文件中
    :param authorization:
    :param cookies:
    :param open_id:
    :return:
    """
    data = {
        'authorization': authorization,
        'cookie': cookies,
        'open_id': open_id
    }
    with open(TARGET_FILE, 'wb') as f:
        pickle.dump(data, f)


def get_param_from_file():
    """
    从文件中获取参数
    :return: 请求头的authorization字段, cookie, open_id（用于标识用户）
    """
    if not os.path.exists(TARGET_FILE):
        return None, None, None
    with open(TARGET_FILE, 'rb') as f:
        data = pickle.load(f)
    logging.debug("成功从文件中读取用户凭证信息: %s", data)
    return data['authorization'], data['cookie'], data['open_id']


def get_param():
    """
    获取参数，首先尝试从文件中，获取成功则直接返回；失败则模拟登录并重新获取参数，该参数将被保存到文件中并返回
    :return:
    """
    authorization, cookie, open_id = get_param_from_file()
    if authorization is not None and cookie is not None and open_id is not None:
        return authorization, cookie, open_id

    # 从文件中获取参数失败 （可能是首次使用程序），模拟登录
    # 获取验证码
    response = s.post(GET_VERIFY_CODE_URL, json=PHONE_NUMBER, headers=headers)
    logging.debug("请求获取验证码的结果: status_code: %d, text: %s", response.status_code, response.text)
    verify_code = input(f"请输入{PHONE_NUMBER}收到的验证码: ")
    # 模拟登录操作
    data = {
        "mobile": PHONE_NUMBER,
        "code": verify_code
    }
    # 登录
    response = s.post(LOGIN_URL, json=data, headers=headers)
    logging.debug("登录请求的结果: status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    # 解析数据
    authorization = data['id']
    # open_id 用于拼接创建订单的URL
    open_id = data['user']['openid']
    save_param_to_file(authorization, s.cookies, open_id)
    return authorization, s.cookies, open_id


def get_remain_time():
    """
    获取洗衣机的最快剩余时间（单位：分钟）
    :return:
    """
    data = {
        "includeDevice": 'true',
        "storeId": STORE_ID
    }
    response = s.post(REMAIN_TIME_URL, json=data, headers=headers)
    logging.debug("获取剩余时间的结果 status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    if len(data['deviceTypeList']) == 0:
        logging.error("获取洗衣机信息失败")
        return
    remain_time = data['deviceTypeList'][0]['minRemaintime']
    logging.info("剩余%d分钟，请稍后重试", int(remain_time))
    return remain_time


def create_order(url_from_qrcode, open_id):
    """
    创建订单（抢洗衣机最重要的逻辑）
    :param open_id:
    :param url_from_qrcode: 从二维码上获取的URL
    :return:
    """
    response = s.get(url_from_qrcode, headers=headers)
    logging.debug("获取洗衣机信息的结果: status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    result = data['result'][0]
    # 创建订单的参数
    data = {
        "payment": 0,
        "deviceWashModelId": 7,
        "storeId": result['storeId'],
        "deviceId": result['virtualId'],
        "selfCleanId": -1
    }
    response = s.post(CREATE_ORDER_URL.format(open_id=open_id), json=data, headers=headers)
    logging.debug("创建订单的结果: status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    if response.status_code == 200:
        logging.info("创建订单成功")
        return True, None
    else:
        logging.info(f"{data['error']['message']}")
        return False, data['error']['message']


# 抢洗衣机
def get_laundry_machine():
    # 获取并更新用户的登录信息
    authorization, cookie, open_id = get_param()
    headers['Authorization'] = authorization
    s.cookies.update(cookie)

    while True:
        # 首先获取当前洗衣机的最快剩余时间。该时间用来调节创建订单失败之后的睡眠时间
        remain_time = get_remain_time()

        # 扫码 获取洗衣机信息(该URL是从二维码中解析出来的)
        for url in LAUNDRY_MACHINE_URLS:
            success, message = create_order(url, open_id)
            if success:
                # 成功抢到洗衣机，发送通知并退出
                notice = Notice()
                notice.send_message(title="成功创建洗衣机订单")
                return
        sleep_time = 0.3
        if remain_time > 7:
            sleep_time = 30
        elif remain_time > 2:
            sleep_time = remain_time
        logging.info(f"睡眠{sleep_time}秒")
        time.sleep(sleep_time)


def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    get_laundry_machine()


"""
抢洗衣机的程序
"""
if __name__ == '__main__':
    # print(get_remain_time())
    main()
