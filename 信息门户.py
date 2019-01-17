#!/usr/bin/python
# coding=utf-8
import time

import requests
from pyquery import PyQuery as pq
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 存储cookie
cookies = {}


def send_email(content):
    # 第三方 SMTP 服务
    mail_host = "smtp.126.com"  # SMTP服务器
    mail_user = "shaojunying1999"  # 用户名
    mail_pass = "shaojunying1999"  # 密码

    sender = 'shaojunying1999@126.com'  # 发件人邮箱
    receivers = ['sjy19990407@qq.com', 'shaojunying@bupt.edu.cn']  # 接收人邮箱

    title = 'The grades have been updated.'  # 邮件主题
    message = MIMEText("sha", 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = Header(title, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print "mail has been send successfully."
    except smtplib.SMTPException as e:
        print e


def parse_cookie():
    """
    :return:
    """
    result = ""
    for cookie in cookies.items():
        result += cookie[0] + "=" + cookie[1] + "; "
    return result


def get_url(url, data=None):
    headers = {
        "Cookie": parse_cookie()
    }
    data = data or {}
    html = requests.get(url, params=data, headers=headers, allow_redirects=False)
    for cookie in html.cookies.items():
        cookies[cookie[0]] = cookie[1]
    return html


def post_url(url, data=None):
    headers = {
        "Cookie": parse_cookie()
    }
    data = data or {}
    html = requests.post(url, data=data, headers=headers, allow_redirects=False)
    for cookie in html.cookies.items():
        cookies[cookie[0]] = cookie[1]
    return html


def login_vpn():
    """
    模拟登陆vpn获得cookies
    """

    """
    首先无参数登陆获得cookies
    """
    get_url("https://vpn.bupt.edu.cn/global-protect/portal/portal.esp")
    get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")
    # get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")
    # get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")
    # get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")

    data = {
        "prot": "https:",
        "server": "vpn.bupt.edu.cn",
        "inputStr": "",
        "action": "getsoftware",
        "user": "2016211967",
        "passwd": "274119",
        "ok": "Log In"
    }

    post_url("https://vpn.bupt.edu.cn/global-protect/login.esp", data=data)
    get_url("https://vpn.bupt.edu.cn/global-protect/portal/portal.esp")
    # get_url("https://vpn.bupt.edu.cn/global-protect/portal/portal.esp")


def login_portal():
    """
    登陆信息门户
    :return:
    """
    # 首先通过登陆vpn获取cookies
    login_vpn()
    html = get_url("https://vpn.bupt.edu.cn/http/my.bupt.edu.cn/")
    html = get_url(html.headers['Location'])
    html = get_url(html.headers['Location'])
    doc = pq(html.text)
    data = {
        "username": "2016211967",
        "password": "04274119",
        "lt": doc("input[name='lt']").attr("value"),
        "execution": doc("input[name='execution']").attr("value"),
        "_eventId": "submit",
        "rmShown": doc("input[name='rmShown']").attr("value"),
    }
    html = post_url(
        "https://vpn.bupt.edu.cn/https/auth.bupt.edu.cn/authserver/login?service=http%3A%2F%2Fmy.bupt.edu.cn%2Flogin"
        ".portal", data=data)
    html = get_url(html.headers['Location'])

    get_url(html.headers['Location'])
    # 访问信息门户
    html = get_url("https://vpn.bupt.edu.cn/http/my.bupt.edu.cn/index.portal")

    # 进入教务系统
    html = get_url("https://vpn.bupt.edu.cn/http-9001/10.3.255.178/caslogin.jsp")
    html = get_url(html.headers['Location'])
    html = get_url(html.headers['Location'])
    html = get_url(html.headers['Location'])
    # 进入成绩查询
    html = get_url("https://vpn.bupt.edu.cn/http-9001/10.3.255.178/bxqcjcxAction.do")
    doc = pq(html.text)
    doc = doc('tr.odd:nth-child(n+1)')
    scores = {}
    num = 0
    for item in doc.items():
        name = item('td:nth-child(3)').text()
        score = item('td:nth-child(7)').text()
        scores[name] = score
        if score == "":
            continue
        num += 1
    result = ""
    for name, score in scores.items():
        result += name.encode("utf-8") + ": " + score + ", "
    print time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), result, "\n\n"

    '''
    文件最后一行存上次更新的全部成绩个数
    倒数第二行存储每门课程对应的成绩
    '''

    with open("result.txt", 'r') as f:
        lines = f.readlines()
        if int(lines[-1]) == num:
            # 说明没有更新
            pass
            return
    with open("result.txt", "w") as f:
        num = 0
        # 说明更新了

        # 将成绩存入文件中
        for _, item in scores.items():
            if item == "":
                continue
            f.write(item + ",")
            num += 1
        f.write("\n" + str(num) + "\n")

        # 将成绩通过邮件发送
        result = result.replace(", ", "\n")
        send_email(result)


login_portal()
