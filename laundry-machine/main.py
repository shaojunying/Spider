import json
import logging
import os
import pickle
import time

import requests

# 获取验证码的链接
GET_VERIFY_CODE_URL = "https://u.zhinengxiyifang.cn/api/CheckCodes/getVerifyCode"
# 要抢洗衣机的手机号
PHONE_NUMBER = "15801692016"
# 登录URL
LOGIN_URL = "https://u.zhinengxiyifang.cn/api/UcleanWechatUsers/loginByMobile"
# 创建订单
CREATE_ORDER_URL = "https://u.zhinengxiyifang.cn/api/UcleanWechatUsers/{open_id}/createOrder"
# 目标文件
TARGET_FILE = "data"
# 查询洗衣机剩余时间
REMAIN_TIME_URL = "https://u.zhinengxiyifang.cn/api/Stores/getStoreDetails"

headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.9(0x18000923) NetType/WIFI Language/zh_CN",
    "Referer": "https://wx.zhinengxiyifang.cn/index.html",
    "Accept-Language": "zh-cn"
}

logging.getLogger().setLevel(logging.INFO)
# 使用session,每次请求会携带之前的cookies
s = requests.session()


# 保存cookie、header到文件中
def save_param_to_file(authorization, cookies, open_id):
    data = {
        'authorization': authorization,
        'cookie': cookies,
        'open_id': open_id
    }
    with open(TARGET_FILE, 'wb') as f:
        pickle.dump(data, f)


def get_param_from_file():
    if not os.path.exists(TARGET_FILE):
        return None, None, None
    with open(TARGET_FILE, 'rb') as f:
        data = pickle.load(f)
    logging.info("成功从文件中读取用户凭证信息: %s", data)
    return data['authorization'], data['cookie'], data['open_id']


def get_param():
    authorization, cookie, open_id = get_param_from_file()
    if authorization is not None and cookie is not None and open_id is not None:
        return authorization, cookie, open_id
    response = s.post(GET_VERIFY_CODE_URL, json=PHONE_NUMBER, headers=headers)
    logging.info("请求获取验证码的结果: status_code: %d, text: %s", response.status_code, response.text)
    verify_code = input("请输入收到的验证码: ")
    # 模拟登录操作
    data = {
        "mobile": PHONE_NUMBER,
        "code": verify_code
    }
    response = s.post(LOGIN_URL, json=data, headers=headers)
    logging.info("登录请求的结果: status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    # 解析数据 抢洗衣机!!!
    authorization = data['id']
    # open_id 用于拼接创建订单的URL
    open_id = data['user']['openid']
    save_param_to_file(authorization, s.cookies, open_id)
    return authorization, s.cookies, open_id


# 抢洗衣机
def get_laundry_machine():
    authorization, cookie, open_id = get_param()
    headers['Authorization'] = authorization
    s.cookies.update(cookie)
    # 扫码 获取洗衣机信息(该URL是从二维码中解析出来的)
    url = "https://u.zhinengxiyifang.cn/api/Devices/getDevicesByCode?qrCode=https:%2F%2Fq.ujing.com.cn%2Fucqrc" \
          "%2Findex.html%3Fcd%3D0000000000000A0007555202104200186164"
    response = s.get(url, headers=headers)
    logging.info("获取洗衣机信息的结果: status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    result = data['result'][0]

    # #
    store_id = '5d490039766c78e720000003'
    # while True:
    data = {
        "includeDevice": 'true',
        "storeId": store_id
    }
    response = s.post(REMAIN_TIME_URL, json=data, headers=headers)
    logging.info("获取剩余时间的结果 status_code: %d, text: %s", response.status_code, response.text)
    data = json.loads(response.text)
    if len(data['deviceTypeList']) == 0:
        logging.error("获取洗衣机信息失败")
        # break
    remain_time = data['deviceTypeList'][0]['minRemaintime']
    if int(remain_time) > 1:
        logging.info("剩余%d分钟，请稍后重试", int(remain_time))
    #         time.sleep(0.8)
    #         continue
    #
    #     # 创建订单的参数
    #     data = {
    #         "payment": 0,
    #         "deviceWashModelId": 7,
    #         "storeId": store_id,
    #         "deviceTypeId": 1,
    #         "selfCleanId": -1
    #     }
    # while True:
    # 创建订单的参数
    data = {
        "payment": 0,
        "deviceWashModelId": 7,
        "storeId": result['storeId'],
        "deviceId": result['virtualId'],
        "selfCleanId": -1
    }
    response = s.post(CREATE_ORDER_URL.format(open_id=open_id), json=data, headers=headers)
    logging.info("创建订单的结果: status_code: %d, text: %s", response.status_code, response.text)


def main():
    get_laundry_machine()


"""
抢洗衣机的程序
"""
if __name__ == '__main__':
    main()
