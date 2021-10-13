import json

import requests

week = 3
day = 7
period = 1
map = {
    0: [1, 2, 3, 4, 5],
    1: [6, 7, 8, 9, 10, 11],
    2: [12, 13, 14]
}
url = "http://name1e5s.fun:4514/free_classrooms?week=%d&day=%d&time=%d"
for period in range(3):
    if period in map.keys():
        result = {}
        for week in range(1, 15):
            for index, time in enumerate(map.get(period)):
                html = requests.get(url % (week, day, time))
                assert html.status_code == 200
                buildings = json.loads(html.text)
                new_result = {}
                for building in buildings:
                    building_name = building["building"]
                    building_classrooms = building["classrooms"]
                    if building_name not in result.keys() or len(result[building_name]) == 0:
                        if index == 0:
                            new_result[building_name] = building_classrooms
                    else:
                        # 集合中保存教师的交集
                        list = []
                        for old_building_classroom in result[building_name]:
                            for new_building_classroom in building_classrooms:
                                if old_building_classroom["name"] == new_building_classroom["name"]:
                                    list.append(new_building_classroom)
                        new_result[building_name] = list
                result = new_result

        print("# 星期%d, %s" % (day, "上午" if period == 0 else "下午" if period == 1 else "晚上"))
        print()
        for building, classrooms in result.items():
            if len(classrooms) == 0:
                continue
            print("## "+building)
            print()
            for classroom in classrooms:
                print(classroom["name"], end=", ")
            print("")

    # pprint.pprint(result)
