import json
import logging.handlers
import os
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests

from config import *

# 获取所有病人列表的URL
PATIENTS_URL = "https://m.hsyuntai.com/med/hp/hospitals/100582/patient/asyncPatientList?t={timestamp}"

# 确定订单的URL
SUBMIT_URL = "https://m.hsyuntai.com/med/hp/hospitals/100582/registration/submit230"

# 登录的URL
LOGIN_URL = "https://m.hsyuntai.com/med/user/100582/login"

# 获取科室详情的URL
DEPARTMENT_URL = "https://m.hsyuntai.com/med/hp/hospitals/100582/registration/doctorDetails225?docId={" \
                 "doctor_id}&filtrate=N"

# 默认的请求头 直接全部传递过去
headers = {
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'DNT': '1',
    'sec-ch-ua-mobile': '?1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/95.0.4638.54 Mobile Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'EagleEye-SessionID': 'tnk8Ivtyd5s7mR941kF996ql2k7p',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-platform': '"Android"',
    'Origin': 'https://m.hsyuntai.com',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5'
}


class Notice:

    def send_message(self, title=None, body=None):
        data = {
            'title': title,
            'body': body
        }
        for url in SEND_NOTICE_URLS:
            response = requests.post(url, data=data)
            logging.debug("%s, %s".format(response.status_code, response.text))


# 使用session可以避免每次请求的时候传递header
s = requests.session()
s.headers.update(headers)
notice = Notice()


def get(url):
    """
    封装了一下get
    :param url:
    :return:
    """
    response = s.get(url)
    logging.debug(f"{response.status_code}\t{response.text}")
    if response.status_code != 200:
        logging.error("程序出现异常，可能网页逻辑发生改动")
        raise Exception("程序出现异常，可能网页逻辑发生改动")
    data = json.loads(response.text)
    if not data['result']:
        logging.warning(f"{data['msg']}")
        raise Exception(f"{data['msg']}")
    return data


def post(url, data):
    """
    封装post
    :param url:
    :param data:
    :return:
    """
    response = s.post(url, json=data)
    logging.debug(f"{response.status_code}\t{response.text}")
    if response.status_code != 200:
        logging.error("程序出现异常，可能网页逻辑发生改动")
        raise Exception("程序出现异常，可能网页逻辑发生改动")
    data = json.loads(response.text)
    return data


def login():
    """
    模拟登录操作，
    :return:
    """
    global s
    data = {
        "username": PHONE,
        "phone": ENCRYPTED_PHONE,
        "password": ENCRYPTED_PASSWORD,
        "login_type": "0"
    }
    data = post(LOGIN_URL, data)
    if not data['result']:
        # 登录失败
        logging.warning(f"{data['result']}")
        raise Exception(f"{data['result']}")
    # 登录成功 保存登录信息
    logging.info("模拟登录成功")
    save_cookies_to_file(s.cookies)


def save_cookies_to_file(cookies):
    """
    保存cookie到文件中
    :return:
    """
    with open(TARGET_FILE, 'wb') as f:
        pickle.dump(cookies, f)


def get_cookies_from_file():
    """
    从文件中获取cookie
    :return: cookie
    """
    if not os.path.exists(TARGET_FILE):
        return None
    with open(TARGET_FILE, 'rb') as f:
        data = pickle.load(f)
    logging.info("成功从文件中读取用户凭证信息")
    return data


def get_patients():
    """
    获取病人的列表
    :return:
    """
    cur_time = int(time.time() * 1000)
    data = get(PATIENTS_URL.format(timestamp=cur_time))
    patients = data['data']

    if len(patients) == 0:
        logging.error("没有可预约的病人")
        return
    logging.debug(patients)
    patients_name_list = [patient['patName'] for patient in patients]
    logging.info(f"已绑定的病人列表 {patients_name_list} ")
    return patients


success = False
# 重复请求
repeated_request = False


def submit(data):
    """
    抢号！！
    :param data:
    :return:
    """
    cur_data = post(SUBMIT_URL, data)
    global success, repeated_request
    if not cur_data['result']:
        if cur_data['msg'] == "每位患者同个排班最多只可预约1次":
            repeated_request = True
        logging.warning(f'{cur_data["msg"]}')
    else:
        success = True
        logging.info(f'成功抢到 {data["deptName"]} 号')


def get_department_info():
    """
    根据doctor_id获取科室信息
    :return:
    """
    response = s.get(DEPARTMENT_URL.format(doctor_id=DOCTOR_ID))
    logging.debug(f"{response.status_code}\t{response.text}")
    if response.status_code != 200:
        raise Exception("程序出现异常，可能网页逻辑发生改动")
    data = json.loads(response.text)
    department_infos = data[2]['data']
    return department_infos


def init_session():
    """
    初始化session 通过data文件或者重新登录
    :return:
    """
    cookies = get_cookies_from_file()
    if cookies is not None:
        # 有之前保存的用户信息 判断信息是否有效
        s.cookies.update(cookies)
        try:
            get_patients()
        except Exception as e:
            logging.info(e)
            # 登录信息已失效，重新登录
            login()
    else:
        # 没有已保存的用户信息，重新登录
        login()


def get_selected_patient():
    """
    获取要抢票的病人信息
    :return:
    """
    patients = get_patients()
    if patients is None or len(patients) == 0:
        logging.error("没有绑定病人，退出程序")
        raise Exception("没有绑定病人，退出程序")
    selected_patient = patients[0]
    if len(patients) == 1:
        logging.info(f"选择病人{selected_patient['patName']}")
    else:
        for patient in patients:
            if patient['patName'] == PATIENT_NAME:
                selected_patient = patient
                break
        else:
            logging.warning(f"没有找到姓名为 {PATIENT_NAME} 的病人，默认选择第一个病人{selected_patient['patName']}")
    return selected_patient


def get_selected_department():
    """
    获取门诊排班信息
    :return:
    """
    department_infos = get_department_info()
    if len(department_infos) == 0:
        logging.error("病人列表为空，无法抢号")
        raise Exception("病人列表为空，无法抢号")
    return department_infos[0]


def init_log_config():
    """
    初始化日志文件配置，将不同级别日志打印到不同的文件中、命令行只展示级别高于或等于info的日志
    :return:
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    debug_handler = logging.FileHandler(os.path.join(LOGGING_PATH, "debug.log"))
    debug_handler.setLevel(logging.DEBUG)

    info_handler = logging.FileHandler(os.path.join(LOGGING_PATH, "info.log"))
    info_handler.setLevel(logging.INFO)

    warning_handler = logging.FileHandler(os.path.join(LOGGING_PATH, "warning.log"))
    warning_handler.setLevel(logging.WARN)

    error_handler = logging.FileHandler(os.path.join(LOGGING_PATH, "error.log"))
    error_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        format='%(asctime)s\t%(pathname)s\tlines: %(lineno)s\t%(levelname)-8s\t%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG,
        handlers=[
            console_handler,
            debug_handler,
            info_handler,
            warning_handler,
            error_handler
        ]
    )


def get_time_from_str(time_str):
    """
    将字符串表示的时间转化为时间对象
    :param time_str:
    :return:
    """
    today = datetime.today().strftime("%Y-%m-%d")
    return datetime.strptime(today + " " + time_str, '%Y-%m-%d %H:%M:%S')


def block_till_tomorrow_if_start_in_night():
    """
    如果是晚上启动的，就先阻塞到第二天
    :return:
    """
    if datetime.now() > get_time_from_str("18:00:00"):
        # 晚上启动的程序，首先睡眠到第二天凌晨
        tomorrow = get_time_from_str("0:0:0") + timedelta(days=1)
        # 晚上启动的程序
        while True:
            now = datetime.now()
            if now >= tomorrow:
                break
            else:
                hour = 1
                notice.send_message(f"当前时间 {now} , 休眠 {hour} 小时")
                logging.info(f"当前时间 {now} , 休眠 {hour} 小时")
                time.sleep(hour * 3600)


def block_until_update_time():
    """
    阻塞，直到当前时间晚于排班更新时间
    :return:
    """
    update_time = get_time_from_str(UPDATE_TIME)
    while True:
        now = datetime.now()
        if now >= update_time:
            break
        else:
            duration = update_time - now
            if duration.seconds > 3600:
                # 剩余时间超过一小时 睡眠一小时之后再重试
                hours = 1
                notice.send_message(f"当前时间 {now} , 早于排班更新时间 {update_time} , 休眠 {hours} 小时")
                logging.info(f"当前时间 {now} , 早于排班更新时间 {update_time} , 休眠 {hours} 小时")
                time.sleep(hours * 3600)
            else:
                # 剩余时间小于1小时 睡眠5分钟
                minutes = 5
                notice.send_message(f"当前时间 {now} , 早于排班更新时间 {update_time} , 休眠 {minutes} 分钟")
                logging.info(f"当前时间 {now} , 早于排班更新时间 {update_time} , 休眠 {minutes} 分钟")
                time.sleep(minutes * 60)


def block_until_create_time():
    """
    阻塞，直到当前时间晚于抢号时间
    :return:
    """
    start_time = get_time_from_str(START_TIME)
    while True:
        now = datetime.now()
        if now >= start_time:
            break
        else:
            duration = start_time - now
            if duration.seconds > 65:
                sleep_time = 60
            else:
                sleep_time = 1
            logging.info(f"当前时间 {now} , 早于开始抢号时间 {start_time} , 休眠 {sleep_time} 秒")
            time.sleep(sleep_time)


def main():
    init_log_config()

    init_session()

    selected_patient = get_selected_patient()

    data = {
        # 下面这五项和病人相关 (从就诊人列表中获取并填充)
        "patId": "xxxxx",
        "patName": "xxx",
        "pcId": "xxxx",
        "patCardType": "xxx",
        "patCardName": "xxx",

        # 这些字段和科室相关 （从获取的科室详情中获取）
        "schId": "xxxxx",  # 这个是要预约的时间
        "deptId": "xxxx",
        "docId": "xxxx",
        "deptName": "xxxx",

        # 一些无关的字段
        "isSendRegSms": "N",
        "type": "0",
        "regSelectItems": {},
        "vcode": "",
        "hosDistId": "",
        "districtId": "",
        "isHealthCard": "false",
        "timeout": "30000",
        "isLoading": "true"
    }

    for key in ('patId', 'patName', 'pcId', 'patCardType', 'patCardName'):
        data[key] = selected_patient[key]

    block_till_tomorrow_if_start_in_night()

    # 当前时间晚于 门诊排班更新时间 时才执行下面的程序
    block_until_update_time()

    notice.send_message("开始获取门诊排班信息")
    logging.info("开始获取门诊排班信息")
    selected_department = get_selected_department()

    # 当前时间晚于 开始时间 时才执行下面的程序
    block_until_create_time()

    end_time = get_time_from_str(END_TIME)
    notice.send_message("开始抢号！！！")
    logging.info("开始抢号！！！")

    for key in ('schId', 'deptId', 'docId', 'deptName'):
        data[key] = selected_department[key]

    # 多线程抢票，避免一个请求耗时过长导致后续请求不能发出。
    global success, repeated_request
    with ThreadPoolExecutor() as pool:
        while True:
            pool.submit(submit, data)
            logging.info(f"休眠 {SLEEP_TIME} 秒")
            time.sleep(SLEEP_TIME)
            now = datetime.now()
            if now >= end_time:
                break
            if success:
                # 成功抢到号
                logging.info("成功抢到号，退出程序")
                break
            if repeated_request:
                # 收到重复请求的提示
                logging.info("收到请求重复的提示，请登录公众号查看结果")
                break

    notice.send_message("结束抢号！！！")


if __name__ == '__main__':
    main()
