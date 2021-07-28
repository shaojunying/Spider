import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

code = "xxxxxxxxxxxxxxxxxxx"
Authorization = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# 迭代的轮数
epoch = 100000

headers = {
    "Host": "dekt.bupt.edu.cn",
    "Connection": "keep-alive",
    "Content-Length": "56",
    "Authorization": Authorization,
    "content-type": "application/json",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x1800072f) NetType/WIFI Language/zh_CN",
}
data = {
    "code": code,
    "actId": 3706
}


def post():
    try:
        response = requests.post("https://dekt.bupt.edu.cn/SecondClassNG/participation/signup", json=data,
                                 headers=headers)
    except requests.Timeout:
        return "time out"
    return response.text


class PostThread(threading.Thread):
    def __init__(self, i):
        super().__init__()
        self.i = i

    def run(self) -> None:
        response = post()
        if True:
            print(datetime.datetime.now().time(), response)


if __name__ == '__main__':
    # print(time.time())
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in range(1000):
            future = executor.submit(post)
            print(datetime.datetime.now().time(), future.result())
    # for i in range(epoch):
    #     thread = PostThread(i)
    #     thread.start()
    #     thread.join()
    #     # time.sleep(0.30)
    # print(time.time())
