#!/usr/bin/python
# coding=utf-8
import requests
from pyquery import PyQuery as pq

# 存储cookie
cookies = {}


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
    get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")
    get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")
    get_url("https://vpn.bupt.edu.cn/global-protect/login.esp")

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
    get_url("https://vpn.bupt.edu.cn/global-protect/portal/portal.esp")


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
    for item in doc.items():
        name = item('td:nth-child(3)').text()
        score = item('td:nth-child(7)').text()
        scores[name] = score
    print(scores)
    with open("result") as f:
        print(f.read())

login_portal()
