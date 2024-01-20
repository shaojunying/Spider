import json
import time
import requests
import datetime
from bs4 import BeautifulSoup
from urllib3 import encode_multipart_formdata
from datetime import date, timedelta
from threading import Thread

# 获取时间
tomorrow = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
today = date.today().strftime("%Y%m%d")

# vip id
# set-part
Cookie = 'pk5otknia7s0pecaf5cbvgblj7'

WebKit = '----WebKitFormBoundaryYB3TXFCsTTvu8qxq'
reverse_time = today
vip_id = xxxxxx
colck_id = '24'
epoch = 1

time_id = reverse_time + colck_id
kw = {
    'area_id': '5985',
    'query_date': reverse_time,
    'td_id': '15415_' + time_id,
    'country_id': '0'
}

data = {
    "custom_class_ids": "",
    "country_id": "",
    "country_name": "",
    "selected_device_name": "",
    "selected_soft_name": "",
    "area_id": "5985",
    "area_name": "健身房",
    "room_id": "15415",
    "room_name": "健身房",
    "device_id": "0",
    "soft_id": "0",
    "time_id": time_id,
    "total_amount": "16",
    "times_arr": "Array",
    "packages_showing_type": "2",
    "mixed_payment_type": "package_pay",
    "to_use_vip_id": vip_id,
    "times_arr_1": "08:00-09:20",
    "times_arr_2": "10:00-11:20",
    "times_arr_3": "12:00-13:20",
    "times_arr_4": "14:00-15:20",
    "times_arr_5": "16:00-17:20",
    "times_arr_6": "18:00-19:20",
    "times_arr_7": "20:00-21:20",
    "times_arr_8": "17:00-18:20",
    "times_arr_9": "19:00-20:20",
    "times_arr_10": "21:00-22:20",
    "times_arr_11": "08:00-09:00",
    "times_arr_12": "09:00-10:00",
    "times_arr_13": "10:00-11:00",
    "times_arr_14": "11:00-12:00",
    "times_arr_15": "12:00-13:00",
    "times_arr_16": "13:00-14:00",
    "times_arr_17": "14:00-15:00",
    "times_arr_18": "15:00-16:00",
    "times_arr_19": "16:00-17:00",
    "times_arr_20": "17:00-18:00",
    "times_arr_21": "18:00-19:00",
    "times_arr_22": "19:00-20:00",
    "times_arr_23": "20:00-21:00",
    "times_arr_24": "21:00-22:00",
    "is_queue": "0",
    "occupy_quota": "1",
    "sign_and_login_type": "1"
}


# s = requests.session()

# 提示在微信客户端登录，暂时不可用
def first_get():
    """获取Cookie地址"""
    headers_0 = {
        'Host': 'reservation.bupt.edu.cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.18 MicroMessenger/7.0.1 Language/zh ColorScheme/Dark',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'zh-CN,zh-Hans;q=0.9'
    }
    url = "https://reservation.bupt.edu.cn/index.php/1600?l=zh-cn"
    requests.get(url, headers=headers_0, verify=False)


def get():
    """获取时间戳"""
    get_headers = {
        'Host': 'reservation.bupt.edu.cn',
        'Cookie': 'PHPSESSID=' + Cookie + '; think_language=zh-CN',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.9 MicroMessenger/7.0.1 Language/zh ColorScheme/Light',
        'accept-language': 'zh-cn',
        'referer': 'https://reservation.bupt.edu.cn/index.php/Wechat/Booking/choose_template/template/1/area_id/5985/country_id/0/from/'
    }
    response = requests.get("https://reservation.bupt.edu.cn/index.php/Wechat/Booking/confirm_booking", params=kw,
                            headers=get_headers, verify=False)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')
    code = soup.input['value']
    # print(code)
    return code


def get_info():
    """获取预约信息"""
    info_url = "https://reservation.bupt.edu.cn/index.php/Wechat/Booking/get_one_day_one_area_state_table_html"

    payload = "now_area_id=5985&query_date=" + reverse_time + "&first_room_id=0&start_date=" + reverse_time + "&the_ajax_execute_times=5"
    get_info_headers = {
        'Host': 'reservation.bupt.edu.cn',
        'Cookie': 'PHPSESSID=' + Cookie + '; think_language=zh-CN',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'zh-CN,zh-Hans;q=0.9',
        'origin': 'https://reservation.bupt.edu.cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.18 MicroMessenger/7.0.1 Language/zh ColorScheme/Light',
        'referer': 'https://reservation.bupt.edu.cn/index.php/Wechat/Booking/choose_template/template/1/area_id/5985/country_id/0/from/'
    }

    response = requests.request("POST", info_url, headers=get_info_headers, data=payload, verify=False)
    dict = json.loads(response.text)
    a = dict['data']['rooms'][0]["already_reserve"][colck_id]
    a = int(a)
    return a


# def engine():
#     """发出语音提示"""
#     engine = pyttsx3.init()
#     engine.say('滴答滴答')
#     engine.runAndWait()


def post(code):
    """发送预约请求"""
    headers_2 = {
        'Host': 'reservation.bupt.edu.cn',
        'Cookie': 'PHPSESSID=' + Cookie + '; think_language=zh-CN',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'content-type': 'multipart/form-data; boundary=' + WebKit,
        'origin': 'https://reservation.bupt.edu.cn',
        'accept-language': 'zh-cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  Mobile/15E148 wxwork/3.1.9 MicroMessenger/7.0.1 Language/zh ColorScheme/Light',
        'referer': 'https://reservation.bupt.edu.cn/index.php/Wechat/Booking/confirm_booking?area_id=5985&td_id=15415_' + time_id + '&query_date=' + reverse_time + '&country_id=0'
    }
    data["form_valid_code_value"] = code
    d = encode_multipart_formdata(data, boundary=WebKit)
    response = requests.post("https://reservation.bupt.edu.cn/index.php/Wechat/Register/register_show",
                             headers=headers_2, data=d[0], verify=False)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')

    return soup.find_all(class_='text')


# Timestamp of the specified time
def get_timestamp_spec_time(clock, days=0):
    """
    获取指定的时间点的时间戳
    :param clock: 钟点;指定的时间,比如当天的凌晨一点,钟点即为1(24小时制)
    :param days:  与当前时间的相差的日期。-1 表示昨天；0 表示当天(默认)；1 表示明天
    :return:      返回时间戳
    """
    nowTime = datetime.datetime.now() + datetime.timedelta(days=days)
    specified_time = nowTime.strftime("%Y-%m-%d") + " {}:00:00".format(clock)
    timeArray = time.strptime(specified_time, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(timeArray))


class Graber(Thread):
    def __init__(self, i):
        super().__init__()
        self.i = i

    def run(self) -> None:
        a = get_info()
        j = 1
        target_second = get_timestamp_spec_time(12)
        curr_second = int(time.time())
        remainder_second = target_second - curr_second
        while reverse_time == tomorrow and remainder_second > 1:
            print("距离开始还有", remainder_second, "秒")
            time.sleep(1)
            target_second = get_timestamp_spec_time(12)
            curr_second = int(time.time())
            remainder_second = target_second - curr_second

        while a == 100:
            time.sleep(1)
            a = get_info()
            print(j, " 已约满")
            j = j + 1
        code = get()
        print(code)
        response = post(code)
        print(i, response)


if __name__ == '__main__':
    for i in range(epoch):
        thread = Graber(i)
        thread.start()
        thread.join()
