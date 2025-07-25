import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Set
import json
import os

def get_course_info():
    url = 'https://webvpn.bupt.edu.cn/http/rerereerererdfqwwew/Gstudent/Course/StudentScoreQuery.aspx'
    
    # 更新查询参数
    params = {
        'EID': 'dxxxxderreerre'
    }
    # 更新请求头中的Cookie
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
        'Connection': 'keep-alive',
        'Cookie': 'show_vpn=0; heartbeat=1; show_faq=0; wengine_vpn_ticketwebvpn_bupt_edu_cn=33223wedswwe; refresh=1',
        'DNT': '1',
        'Referer': 'https://webvpn.bupt.edu.cn/http/w4ew4323242322323ewadsaewe323/Gstudent/LeftMenu.aspx',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def parse_course_info(html_content) -> Dict[str, dict]:
    """解析课程信息并返回字典格式的数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='contentParent_dgData')
    
    if not table:
        print(html_content)
        print("未找到成绩表格")
        return {}
    
    courses = {}
    rows = table.find_all('tr')[1:]  # 跳过表头行
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 7:
            course_name = cols[1].text.strip()
            courses[course_name] = {
                'final_score': cols[5].text.strip(),
                'total_score': cols[6].text.strip(),
                'rank': cols[7].text.strip()
            }
    
    return courses

def print_courses(courses: Dict[str, dict]):
    """打印课程信息"""
    print("\n=== 课程成绩信息 ===")
    print("课程名称".ljust(40) + "期末成绩".ljust(10) + "综合成绩".ljust(10) + "班级排名")
    print("-" * 80)
    
    for course_name, info in courses.items():
        print(f"{course_name.ljust(40)} {info['final_score'].ljust(10)} {info['total_score'].ljust(10)} {info['rank']}")

def save_courses(courses: Dict[str, dict]):
    """保存课程信息到文件"""
    with open('../courses.json', 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

def load_courses() -> Dict[str, dict]:
    """从文件加载课程信息"""
    if not os.path.exists('../courses.json'):
        return {}
    with open('../courses.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def check_new_courses(old_courses: Dict[str, dict], new_courses: Dict[str, dict]) -> Set[str]:
    """检查是否有新的课程成绩"""
    old_course_names = set(old_courses.keys())
    new_course_names = set(new_courses.keys())
    return new_course_names - old_course_names

def send_notification(new_courses: Set[str], courses: Dict[str, dict]):
    """
    使用FWAlert发送通知，为每门新课程单独发送通知
    """
    notification_url = "https://fwalert.com/223ewsddssd"
    
    # 遍历所有新增课程并逐个发送通知
    for course in new_courses:
        info = courses[course]
        message = f"{course[:8]}..{info['total_score']}分"  # 课程名过长时截断
        
        try:
            response = requests.get(notification_url, params={'message': message})
            response.raise_for_status()
            print(f"课程 {course} 的通知发送成功！")
        except Exception as e:
            print(f"发送通知时出错：{e}")

def send_all_courses(courses: Dict[str, dict]):
    """
    发送所有课程信息，控制消息在20字以内
    """
    message = f"已出{len(courses)}门课程成绩"
    
    # 发送通知
    notification_url = "https://fwalert.com/a92d2628-fcb2-4326-ac43-d7dd3d8abfaa"
    try:
        response = requests.get(notification_url, params={'message': message})
        response.raise_for_status()
        print("启动通知发送成功！")
    except Exception as e:
        print(f"发送启动通知时出错：{e}")

def monitor_courses(interval: int = 30):
    """
    监控课程成绩变化
    :param interval: 检查间隔时间（秒）
    """
    print(f"开始监控课程成绩，每{interval}秒检查一次...")
    
    # # 获取当前所有成绩并打印
    # result = get_course_info()
    # if result:
    #     current_courses = parse_course_info(result)
    #     if current_courses:
    #         print(f"\n当前已出{len(current_courses)}门课程成绩：")
    #         print_courses(current_courses)
    #         save_courses(current_courses)
    
    while True:
        try:
            # 加载之前保存的课程信息
            old_courses = load_courses()
            
            # 获取最新课程信息
            result = get_course_info()
            if not result:
                print("获取课程信息失败，2分钟后重试...")
                time.sleep(interval)
                continue
                
            new_courses = parse_course_info(result)
            
            # 检查新增的课程
            new_course_names = check_new_courses(old_courses, new_courses)
            
            if new_course_names:
                print("\n发现新的成绩！")
                print("新增课程：", ", ".join(new_course_names))
                print_courses(new_courses)
                
                # 发送通知
                send_notification(new_course_names, new_courses)
                
                # 保存最新的课程信息
                save_courses(new_courses)
            else:
                print("\r最后检查时间：", time.strftime("%Y-%m-%d %H:%M:%S"), end="")
            
            time.sleep(interval)
            
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("30秒后重试...")
            time.sleep(interval)

if __name__ == "__main__":
    monitor_courses()
