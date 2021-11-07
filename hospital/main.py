import json
import logging.handlers
import os
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor

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

# 使用session可以避免每次请求的时候传递header
s = requests.session()
s.headers.update(headers)


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
    if not data['result']:
        logging.warning(f"{data['msg']}")
        raise Exception(f"{data['msg']}")
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


def submit(data):
    """
    抢号！！
    :param data:
    :return:
    """
    try:
        cur_data = post(SUBMIT_URL, data)
    except Exception:
        return

    if not cur_data['result']:
        logging.warning(f'{cur_data["message"]}')
    logging.info(f'成功抢到 {data["deptName"]} 号')


def get_department_info():
    """
    根据doctor_id获取科室信息
    :return:
    """
    response = s.get(DEPARTMENT_URL.format(doctor_id=DOCTOR_ID))
    logging.debug(f"{response.status_code}\t{response.text}")
    if response.status_code != 200:
        logging.error("程序出现异常，可能网页逻辑发生改动")
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


# 选中的科室信息
selected_department = None


def parse_department_info():
    """
    解析获取到的部门信息，如果不是11-05的日期，就赋值给selected_department并退出
    :return:
    """
    global selected_department
    department_infos = get_department_info()
    for department_info in department_infos:
        logging.info(f"获取到了 {department_info['deptName']} 科室 {department_info['schDate']}  的抢号链接")
        if department_info['schDate'] == '11-05':
            logging.info("获取到的抢号链接日期是 11-05")
        else:
            selected_department = department_info
            break


def get_selected_department():
    """
    多线程获取排班信息，同样避免一个请求阻塞掉后续请求的发出。
    一旦这个函数正常退出，selected_department就已经被正常赋值了。
    :return:
    """
    global selected_department
    with ThreadPoolExecutor() as pool:
        while selected_department is None:
            pool.submit(parse_department_info)
            if SLEEP_TIME > 0:
                logging.info(f"休眠 {SLEEP_TIME} 秒后继续重试")
                time.sleep(SLEEP_TIME)
            break


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

    global selected_department
    get_selected_department()

    logging.info("获取到的抢号链接日期不是 11-05，开始抢号！！！")

    for key in ('schId', 'deptId', 'docId', 'deptName'):
        data[key] = selected_department[key]

    # 多线程抢票，避免一个请求耗时过长导致后续请求不能发出。
    with ThreadPoolExecutor() as pool:
        while True:
            pool.submit(submit, data)
            if SLEEP_TIME > 0:
                logging.info(f"休眠 {SLEEP_TIME} 秒")
                time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
