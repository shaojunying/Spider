import re
import time

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "ASP.NET_SessionId=u1zxlhxrl2004tvqievfqumw; DropDownListXqu=",
    "DNT": "1",
    "Host": "10.3.255.31",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/85.0.4183.102 "
                  "Safari/537.36",
}

target_courses_id = "3151400056"


def log(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\t" + message)


def simulate_select_class_page(param):
    """
    模拟点击选择上课班级的页面,获取提交选课请求时需要的表单
    :return:
    """
    # 模拟点击"选择上课班级按钮"
    choose_class_url = "http://10.3.255.32/Gstudent/Course/PlanSelClass.aspx?" + param
    html = requests.get(choose_class_url, headers=headers)
    assert html.status_code == 200
    soup = BeautifulSoup(html.text, "lxml")
    # 提交选课请求时要用的表单
    return {
        "ctl00$ScriptManager1": soup.select_one('input[title="选择课程班级"]'),
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": soup.select_one("#__VIEWSTATE")["value"],
        "__VIEWSTATEGENERATOR": soup.select_one("#__VIEWSTATEGENERATOR")["value"],
        "__VIEWSTATEENCRYPTED": soup.select_one("#__VIEWSTATEENCRYPTED")["value"],
        "__EVENTVALIDATION": soup.select_one("#__EVENTVALIDATION")["value"],
        "__ASYNCPOST": "true",
        "ctl00$contentParent$drpXqu$drpXqu": "",
        "ctl00$contentParent$dgData$ctl02$ImageButton1.x": "8",
        "ctl00$contentParent$dgData$ctl02$ImageButton1.y": "8"
    }


def confirm_select_course_result(target_course_id):
    html = requests.get("http://10.3.255.32/Lesson/PlanCourseOnlineSel.aspx", headers=headers)
    assert html.status_code == 200, "获取计划课程列表失败"
    soup = BeautifulSoup(html.text, "lxml")
    trs = soup.select("#contentParent_dgData > tr")

    # 第一项为表头
    for i in range(1, len(trs)):
        course_property = trs[i].select("td")
        course_id = course_property[0].get_text().course_status()
        course_status = trs[i].select("a")[0].get_text().course_status()
        if course_id == target_course_id:
            return course_status != "选择上课班级" and course_status != ""
    return False


while True:

    html = requests.get("http://10.3.255.32/Lesson/PlanCourseOnlineSel.aspx", headers=headers)
    assert html.status_code == 200, "获取计划课程列表失败"

    soup = BeautifulSoup(html.text, "lxml")

    trs = soup.select("#contentParent_dgData > tr")

    # 第一项为表头
    for i in range(1, len(trs)):
        course_property = trs[i].select("td")
        course_id = course_property[0].get_text().strip()
        course_name = course_property[1].get_text().strip()
        # 获取课程状态
        links = trs[i].select("a")
        if len(links) == 1:
            selection_status = ""
            course_status = trs[i].select("a")[0].get_text().strip()
        else:
            selection_status = links[0].get_text().strip()
            course_status = trs[i].select("a")[1].get_text().strip()

        if course_status != "班级已全选满":
            log("课程[%s]还有余量" % course_name)

        if course_id == target_courses_id:
            if selection_status != "选择上课班级" and selection_status != "":
                log("您当前已经选择课程[%s]" % course_name)
            elif course_status == "班级已全选满":
                log("要选的课程[%s]已全选满" % course_name)
            else:
                log("开始选择课程[%s]" % course_name)
                # 获取选课请求需要的参数
                text = trs[i].select("a")[0]["onclick"]
                result = re.search(r"selClass\('\?(.*?)','selClass'\);", text)
                if result is not None:
                    param = result.group(1)
                    # 提交选课请求时要用的表单
                    data = simulate_select_class_page(param)

                    select_course_url = "http://10.3.255.32/Gstudent/Course/PlanSelClass.aspx?" + param
                    result = requests.post(select_course_url, data=data, headers=headers)
                    while result.status_code != 200 or not confirm_select_course_result(target_courses_id):
                        log("选课[%s]失败,将在1秒之后重试" % course_name)
                        time.sleep(1)
                        result = requests.post(select_course_url, data=data, headers=headers)
                    else:
                        log("选择课程[%s]成功" % course_name)
    time.sleep(3)
    print("\n\n\n")
