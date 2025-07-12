# import subprocess
# from typing import List, Dict
#
# import requests
# import logging
#
# from bs4 import BeautifulSoup
#
# # 配置 logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("request.log"),  # 将日志写入文件
#         logging.StreamHandler()  # 同时输出到控制台
#     ]
# )
#
#
# def fetch_races_results(page=1, season_id=1000058):
#     # Build the curl command
#     curl_command = f"""
#         curl 'https://www.ibsf.org/en/races-and-results?tx_fmresults_list%5B__referrer%5D%5B%40extension%5D=FmResults&tx_fmresults_list%5B__referrer%5D%5B%40controller%5D=List&tx_fmresults_list%5B__referrer%5D%5B%40action%5D=main&tx_fmresults_list%5B__referrer%5D%5Barguments%5D=YTo1OntzOjg6ImV2ZW50X2lkIjtzOjY6IjIwMDgwNSI7czo5OiJzZWFzb25faWQiO3M6NzoiMTAwMDA1OCI7czoxNjoic2Vzc2lvbl90eXBlX2lkcyI7czowOiIiO3M6NToic3BvcnQiO3M6MDoiIjtzOjk6InRyYWluaW5ncyI7czowOiIiO30%3D2670891da94a255eae808865873926cf44797536&tx_fmresults_list%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22FmResults%22%2C%22%40controller%22%3A%22List%22%2C%22%40action%22%3A%22main%22%7D2f4e45e169d2363ac0f69e19bf11567a60cdc86d&tx_fmresults_list%5B__trustedProperties%5D=%7B%22sport%22%3A1%2C%22season_id%22%3A1%2C%22session_type_ids%22%3A1%2C%22event_id%22%3A1%2C%22trainings%22%3A1%7Dc7a3c325f8425ead471e0c6286b082a9f6d6f280&tx_fmresults_list%5Bsport%5D=&tx_fmresults_list%5Bseason_id%5D=1000058&tx_fmresults_list%5Bsession_type_ids%5D=&tx_fmresults_list%5Bevent_id%5D=&tx_fmresults_list%5Btrainings%5D=' \
#           -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
#           -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
#           -H 'Connection: keep-alive' \
#           -b 'CookieConsent={{stamp:%27u/N+CtcVPkVu1rBjb0Ovs7L3DqLH6DJ9FWks2tg8H2FIPsUOsT3dcg==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1739507464091%2Cregion:%27us-04%27}}; _ga=GA1.1.1788691894.1739507465; _ga_GNFJNB5XFQ=GS1.1.1740633448.6.1.1740633549.0.0.0' \
#           -H 'DNT: 1' \
#           -H 'Referer: https://www.ibsf.org/en/races-and-results?tx_fmresults_list%5B__referrer%5D%5B%40extension%5D=FmResults&tx_fmresults_list%5B__referrer%5D%5B%40controller%5D=List&tx_fmresults_list%5B__referrer%5D%5B%40action%5D=main&tx_fmresults_list%5B__referrer%5D%5Barguments%5D=YToyOntzOjQ6InBhZ2UiO3M6MToiMSI7czo5OiJzZWFzb25faWQiO3M6NzoiMTAwMDA1OCI7fQ%3D%3Db9b4bd9bfd46026834273cbb41ac58e8c17a95a0&tx_fmresults_list%5B__referrer%5D%5B%40request%5D=%7B%22%40extension%22%3A%22FmResults%22%2C%22%40controller%22%3A%22List%22%2C%22%40action%22%3A%22main%22%7D2f4e45e169d2363ac0f69e19bf11567a60cdc86d&tx_fmresults_list%5B__trustedProperties%5D=%7B%22sport%22%3A1%2C%22season_id%22%3A1%2C%22session_type_ids%22%3A1%2C%22event_id%22%3A1%2C%22trainings%22%3A1%7Dc7a3c325f8425ead471e0c6286b082a9f6d6f280&tx_fmresults_list%5Bsport%5D=&tx_fmresults_list%5Bseason_id%5D=1000058&tx_fmresults_list%5Bsession_type_ids%5D=&tx_fmresults_list%5Bevent_id%5D=200805&tx_fmresults_list%5Btrainings%5D=' \
#           -H 'Sec-Fetch-Dest: document' \
#           -H 'Sec-Fetch-Mode: navigate' \
#           -H 'Sec-Fetch-Site: same-origin' \
#           -H 'Sec-Fetch-User: ?1' \
#           -H 'Upgrade-Insecure-Requests: 1' \
#           -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36' \
#           -H 'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"' \
#           -H 'sec-ch-ua-mobile: ?0' \
#           -H 'sec-ch-ua-platform: "macOS"'
#         """
#
#     logging.info(f"Fetching data")
#     result = subprocess.run(
#         curl_command,
#         shell=True,
#         check=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#
#     if result.returncode != 0:
#         logging.error(f"Curl command failed with error: {result.stderr}")
#         raise Exception(f"Curl command failed: {result.stderr}")
#
#     return result.stdout
#
# def parse_html(html):
#     soup = BeautifulSoup(html, 'lxml')
#     results = []
#
#     # 找到所有的<tr>元素
#     tr_elements = soup.find_all('tr', class_='sport-bs')
#
#     for tr in tr_elements:
#         competition = {}
#
#         # 提取competition-id和uri
#         competition_id = tr.get('data-competition-id')
#         uri = tr.get('data-uri')
#         competition['competition_id'] = competition_id if competition_id else None
#         competition['uri'] = uri if uri else None
#
#         # 提取日期和时间
#         date_time_td = tr.find('td', class_='resultBlock__col--competition-date')
#         if date_time_td:
#             date_local_span = date_time_td.find('span', {'data-format': 'date'})
#             time_local_span = date_time_td.find('span', {'data-format': 'time'})
#             competition['date_local'] = date_local_span.get('data-datelocal') if date_local_span else None
#             competition['time_local'] = time_local_span.get('data-datelocal') if time_local_span else None
#         else:
#             competition['date_local'] = None
#             competition['time_local'] = None
#
#         # 提取比赛类型
#         session_type_td = tr.find('td', class_='resultBlock__col--competition-sessiontype')
#         competition['session_type'] = session_type_td.find('p').get_text(
#             strip=True) if session_type_td and session_type_td.find('p') else None
#
#         # 提取项目名称
#         event_td = tr.find('td', class_='text-center')
#         if event_td:
#             event_icon = event_td.find('i', class_='svg--sporticon')
#             event_name = event_td.find('div', class_='text-small')
#             competition['event'] = f"{event_icon.get('class')[0].replace('svg-', '')} {event_name.get_text(strip=True)}" \
#                 if event_icon and event_name else None
#         else:
#             competition['event'] = None
#
#         # 提取地点
#         location_tds = tr.find_all('td', class_='text-center')
#         if len(location_tds) > 3:
#             location_td = location_tds[3]
#             country_flag = location_td.find('img', class_='flag')
#             location_name = location_td.find('div', class_='text-small')
#             competition[
#                 'location'] = f"{country_flag['src'].split('/')[-1].split('.')[0] if country_flag else ''} {location_name.get_text(strip=True) if location_name else ''}"
#         else:
#             competition['location'] = None
#
#         # 提取结果链接
#         results_link_td = tr.find('td', class_='resultBlock__col--competition-buttons')
#         competition['results_link'] = results_link_td.find('a')['href'] if results_link_td and results_link_td.find(
#             'a') else None
#
#         results.append(competition)
#
#     return results
#
# def main():
#     html_content = fetch_races_results()
#     if html_content:
#         races = parse_html(html_content)
#         for idx, race in enumerate(races, 1):
#             logging.info(f"赛事 {idx}: {race}")
#             # 这里可以进一步处理每条赛事信息，例如存储到数据库或写入文件
#
# if __name__ == "__main__":
#     main()