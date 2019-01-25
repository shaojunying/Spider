import json

import requests

s = requests.Session()
response = s.get("https://vpn.bupt.edu.cn/global-protect/portal/portal.esp")
cookies = response.cookies.get_dict()
print cookies
cookies_json = json.dumps(cookies, ensure_ascii=False, encoding='utf-8')
with open("cookie.json", "w") as f:
    f.write(cookies_json)
cookie_json = []
with open("cookie.json", "r") as f:
    cookie_json = f.read()
print yaml.safe_load(cookie_json)
