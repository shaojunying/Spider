import datetime
import errno
import json
import os
from concurrent.futures import ThreadPoolExecutor
from urllib import parse

import requests
from dateutil.relativedelta import relativedelta

start_time = "2019-01-19"
end_time = "2022-01-19"

pdf_dir = "todo"

download_type = "中小板"
# download_type = "创业板"
# download_type = "科创板"

condition = {
    "中小板": {
        "plate": "szmb",
        "prefix": "002",
    },
    "创业板": {
        "plate": "szcy"
    },
    "科创板": {
        "plate": "shkcp"
    },
}


def download_PDF(url, file_path):  # 下载pdf
    print("正在下载：" + url, "保存目录为：" + file_path)
    url = url
    r = requests.get(url)
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(file_path, 'wb') as f:
        f.write(r.content)


def get_PDF(trade: str, page: int, pool, total_page, date):  # 获取pdf
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        'stock': '',
        'tabName': 'fulltext',
        'pageSize': 30,
        'pageNum': page,
        'column': 'szse',
        'category': 'category_ndbg_szsh;',
        'plate': condition[download_type]['plate'],
        'seDate': date,
        'searchkey': '',
        'secid': '',
        'sortName': '',
        'sortType': '',
        'isHLtitle': 'true',
        'trade': trade
    }

    hd = {
        'Host': 'www.cninfo.com.cn',
        'Origin': 'http://www.cninfo.com.cn',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip,deflate',
        'Connection': 'keep-alive',
        'User-Agent': 'User-Agent:Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json,text/plain,*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = parse.urlencode(data)
    r = requests.post(url, headers=hd, data=data)
    r = str(r.content, encoding="utf-8")
    try:
        r = json.loads(r)
    except:
        print(r)
        print("解析json出错")
        return
    reports_list = r['announcements']
    print("第" + str(page) + "页，共" + str(total_page) + "页")
    if page > 100:
        print(reports_list)
    for report in reports_list:
        if '摘要' in report['announcementTitle'] or "20" not in report['announcementTitle']:
            continue
        company_name = report['secName']
        company_code = report['secCode']
        if 'prefix' in condition[download_type] and company_code[0:3] != condition[download_type]['prefix']:
            continue
        # 删除已取消的
        if '（已取消）' in report['announcementTitle']:
            continue
        # 删除英文版的
        if '（英文版）' in report['announcementTitle']:
            continue
        # http://static.cninfo.com.cn/finalpage/2019-03-29/1205958883.PDF
        pdf_url = "http://static.cninfo.com.cn/" + report['adjunctUrl']
        file_name = report['announcementTitle']
        file_path = f"{pdf_dir}/{trade}/{company_code}--{company_name}/{file_name}.pdf"
        if os.path.exists(file_path):
            continue
        pool.submit(download_PDF, pdf_url, file_path)


def getCount(trade: str, date):
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        'stock': '',
        'tabName': 'fulltext',
        'pageSize': 100,
        'pageNum': 1,
        'column': 'szse',
        'category': 'category_ndbg_szsh;',
        'plate': condition[download_type]['plate'],
        'seDate': date,
        'searchkey': '',
        'secid': '',
        'sortName': '',
        'sortType': '',
        'isHLtitle': 'true',
        'trade': trade
    }

    hd = {
        'Host': 'www.cninfo.com.cn',
        'Origin': 'http://www.cninfo.com.cn',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip,deflate',
        'Connection': 'keep-alive',
        'User-Agent': 'User-Agent:Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json,text/plain,*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = parse.urlencode(data)
    r = requests.post(url, headers=hd, data=data)
    r = str(r.content, encoding="utf-8")
    try:
        r = json.loads(r)
    except:
        print(r)
        print("解析json出错")
        return
    return int(r['totalRecordNum'])


if __name__ == '__main__':
    trades = ["农、林、牧、渔业", "电力、热力、燃气及水生产和供应业", "交通运输、仓储和邮政业", "金融业", "科学研究和技术服务业",
              "教育", "综合", "卫生和社会工作", "水利、环境和公共设施管理业", "房地产业", "住宿和餐饮业", "建筑业", "采矿业",
              "批发和零售业", "信息传输、软件和信息技术服务业", "租赁和商务服务业", "居民服务、修理和其他服务业", "文化、体育和娱乐业"
              ]
    with ThreadPoolExecutor() as pool:
        for trade in trades:
            count = getCount(trade, start_time + "~" + end_time)
            if count > 3000:
                print("页面太多了")
                continue
            for page in range(1, (count + 29) // 30 + 1):
                get_PDF(trade, page, pool, (count + 29) // 30, start_time + "~" + end_time)

    # 单独处理制造业
    with ThreadPoolExecutor(max_workers=100) as pool:
        trade = "制造业"
        end = datetime.datetime.strptime(end_time + " 00:00:00", '%Y-%m-%d %H:%M:%S').date()
        start = datetime.datetime.strptime(start_time + " 00:00:00", '%Y-%m-%d %H:%M:%S').date()
        cur = start
        while cur < end:
            date = str(cur) + "~" + str(cur + relativedelta(months=+1))
            print(date)
            count = getCount(trade, date=date)
            if count > 3000:
                print("页面太多了")
                continue
            for page in range(1, (count + 29) // 30 + 1):
                get_PDF(trade, page, pool, (count + 29) // 30, date)
            cur = cur + relativedelta(months=+1)
    print("All done!")
