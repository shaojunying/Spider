#!/usr/bin/env python3
# -*- coding: utf-8 -*
import argparse
import json
import logging
import os.path
import pickle
import setting as S
from flask import Flask, request, render_template

import requests

door_map = {
    "单元门": "231516322133987328",
    "西门": "238761945098878976",
    "东一门": "238774987446550528",
    "东二门": "238773766216220672",
}

params = {
    "password": S.encrypted_password,
    "deviceId": S.device_id,
    "loginNumber": S.login_number,
    "equipmentFlag": "1"
}

# 获取用于加密的key
GET_PASSWORD_AES_KEY_URL = "https://api.lookdoor.cn:443/func/hjapp/user/v2/getPasswordAesKey.json?"

# 登录
LOGIN_URL = "https://api.lookdoor.cn:443/func/hjapp/user/v2/login.json"

# 开门
OPEN_DOOR_URL = "https://api.lookdoor.cn:443/func/hjapp/house/v1/pushOpenDoorBySn.json?equipmentId={equipment_id}"

LOGIN_RETURN_VALUES_URL = "https://api.lookdoor.cn:443/func/hjapp/user/v1/loginReturnValues.json?"

# 默认要开启的门（没有在命令行指定的话将开这个门）
DOOR = "单元门"

# 用于保存登录信息的文件的文件名
TARGET_FILE = "data"

header = {
    "accept": "*/*",
    "content-type": "text/json;charset=utf-8",
    "user-agent": "%E5%AE%88%E6%9C%9B%E9%A2%86%E5%9F%9F/2.6.2.14 CFNetwork/1240.0.4 Darwin/20.5.0",
    "accept-language": "zh-cn",
    "accept-encoding": "gzip, deflate, br"
}


def save_data_to_file(data, file=TARGET_FILE):
    """
    将数据保存到文件中
    :param data:
    :param file:
    :return:
    """
    with open(file, 'wb') as f:
        pickle.dump(data, f)


def load_data_from_file(file=TARGET_FILE):
    """
    从文件中加载数据
    :param file:
    :return:
    """
    if os.path.exists(file):
        with open(file, "rb") as f:
            cookie = pickle.load(f)
            return cookie


def login():
    """
    模拟《守望领域APP的登录请求》
    :return:
    """
    session = requests.session()

    # 这个请求是为了获取一个新的session_id
    response = session.post(GET_PASSWORD_AES_KEY_URL)
    logging.info(f"GET_PASSWORD_AES_KEY_URL response:{response.text}")

    response = session.post(LOGIN_URL, params=params)
    logging.info(f"LOGIN_URL response:{response.text}")

    save_data_to_file(session.cookies)


def get_login_return_value(session:requests.Session):
    response = session.post(LOGIN_RETURN_VALUES_URL)
    data = json.loads(response.text)
    logging.info(f"LOGIN_RETURN_VALUES_URL response:{response.text}")
    if data['code'] != 200:
        logging.error(f"获取登录信息失败")
        return None
    data = data['data']
    if len(data) == 0:
        logging.error(f"获取登录信息失败")
        return None
    return data['blockList'][0]['openDoorPwd']


def open_the_door(door, retry_when_login_ticket_expired=False):
    """
    尝试开门，如果开门失败 并且 retry_when_login_ticket_expired 为True则登录后再次尝试；否则直接退出
    :param door:
    :param retry_when_login_ticket_expired: 登录信息失效之后是否重新重试
    :return:
    """
    # 尝试开门
    session = requests.session()

    # 从文件中加载cookie
    cookie = load_data_from_file()
    if cookie is not None:
        session.cookies.update(cookie)

    response = session.post(OPEN_DOOR_URL.format(equipment_id=door_map.get(door)), headers=header)
    data = json.loads(response.text)
    logging.info(f"开门：code: {data['code']}, message: {data['message']}")
    if data['code'] == 200:
        # 成功
        logging.info(f"开锁[{door}]成功")
        return False, f"开锁[{door}]成功"
    elif data['code'] == 999:
        password = get_login_return_value(session)
        logging.info(f"password: {password}")
        return True, password
    elif data['code'] == 2:
        # 登录信息失效，重新登录
        logging.error("登录信息失效")
        if not retry_when_login_ticket_expired:
            return False, f"登录信息失效"
        # 重新登录并开门
        logging.info("重新登录")
        login()
        return open_the_door(door, False)
    else:
        logging.error(f"开门失败：code: {data['code']}, message: {data['message']}")
        return False, f"开门失败：code: {data['code']}, message: {data['message']}"


def main():
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--door")

    args = parser.parse_args()
    door = DOOR
    if args.door:
        input_door = args.door
        if input_door not in door_map.keys():
            logging.error(f"请输入以下门类型的一种: [ {','.join(door_map.keys())} ]")
            return
        door = args.door
    logging.info(f"尝试开门{door}")

    open_the_door(door, True)


# 创建一个接口 暴露main函数
app = Flask(__name__)


@app.route("/")
def index():
    door = request.args.get("door", default="单元门")
    should_use_password, message = open_the_door(door, retry_when_login_ticket_expired=True)
    if should_use_password:
        return render_template("show_password.html", password=message)
    else:
        return render_template("index.html", message=message)


if __name__ == '__main__':
    open_the_door("单元门", retry_when_login_ticket_expired=True)
    app.run("0.0.0.0", port=80)
