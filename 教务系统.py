"""
首先无参get教务系统,获得cookies
"""
import requests
import matplotlib.pyplot as plt

url = "https://webvpn.bupt.edu.cn/http/jwxt.bupt.edu.cn/"
html = requests.get(url)
cookie = html.headers['Set-Cookie'].split(';')[0]
url = "https://webvpn.bupt.edu.cn/wengine-auth/dologin/?from=webvpn.bupt.edu.cn/http/jwxt.bupt.edu.cn/"
data = {
    "auth_type": "local",
    "username": "2016211967",
    "sms_code": "",
    "password": "274119"
}
headers = {
    "cookie": cookie
}
html = requests.post(url, data=data, headers=headers)
print(html.text)
