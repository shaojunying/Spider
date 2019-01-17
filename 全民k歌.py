import requests
from pyquery import PyQuery as pq

url = 'https://node.kg.qq.com/personal?uid=639c9580272f3e8332'
html = requests.get(url)
doc = pq(html.text)
list = doc('#songs-list > li > div > a')
for item in list.items():
    print(item.attr('href'))

