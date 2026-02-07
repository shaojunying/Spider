import re
from bs4 import BeautifulSoup
import json
import pandas as pd


def parse_property_listings(html_content):
    """
    解析房源列表HTML内容
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到所有房源条目
    properties = soup.find_all('div', class_='property')

    property_list = []

    for prop in properties:
        try:
            # 提取基本信息
            property_data = {}

            # 标题
            title_elem = prop.find('h3', class_='property-content-title-name')
            if title_elem:
                property_data['title'] = title_elem.get('title', '').strip()

            # 户型信息
            attr_elem = prop.find('p', class_='property-content-info-attribute')
            if attr_elem:
                spans = attr_elem.find_all('span')
                if len(spans) >= 6:
                    property_data['rooms'] = spans[0].text.strip()
                    property_data['living_rooms'] = spans[2].text.strip()
                    property_data['bathrooms'] = spans[4].text.strip()
                    property_data['layout'] = f"{spans[0].text}室{spans[2].text}厅{spans[4].text}卫"

            # 面积
            info_texts = prop.find_all('p', class_='property-content-info-text')
            for text in info_texts:
                content = text.text.strip()
                if '㎡' in content:
                    property_data['area'] = content.replace('㎡', '').strip()
                elif content in ['南北', '南', '北', '东西']:
                    property_data['orientation'] = content
                elif '层' in content and '共' in content:
                    property_data['floor_info'] = content
                elif '年建造' in content:
                    property_data['build_year'] = content.replace('年建造', '').strip()

            # 小区名称
            comm_name = prop.find('p', class_='property-content-info-comm-name')
            if comm_name:
                property_data['community'] = comm_name.text.strip()

            # 地址
            comm_address = prop.find('p', class_='property-content-info-comm-address')
            if comm_address:
                address_parts = [span.text.strip() for span in comm_address.find_all('span')]
                property_data['district'] = address_parts[0] if len(address_parts) > 0 else ''
                property_data['area_name'] = address_parts[1] if len(address_parts) > 1 else ''
                property_data['detailed_address'] = address_parts[2] if len(address_parts) > 2 else ''

            # 价格信息
            price_total = prop.find('span', class_='property-price-total-num')
            if price_total:
                property_data['total_price'] = price_total.text.strip() + '万'

            price_avg = prop.find('p', class_='property-price-average')
            if price_avg:
                property_data['price_per_sqm'] = price_avg.text.strip()

            # 链接
            link_elem = prop.find('a')
            if link_elem:
                property_data['url'] = link_elem.get('href', '')

            property_list.append(property_data)

        except Exception as e:
            print(f"解析房源时出错: {e}")
            continue

    return property_list


def analyze_properties(properties):
    """
    分析房源数据
    """
    if not properties:
        return {}

    # 提取价格数据进行分析
    prices = []
    areas = []
    price_per_sqm = []

    for prop in properties:
        try:
            if 'total_price' in prop:
                price = float(prop['total_price'].replace('万', ''))
                prices.append(price)

            if 'area' in prop:
                area = float(prop['area'])
                areas.append(area)

            if 'price_per_sqm' in prop:
                price_sqm = float(prop['price_per_sqm'].replace('元/㎡', '').replace(',', ''))
                price_per_sqm.append(price_sqm)
        except:
            continue

    analysis = {
        'total_properties': len(properties),
        'price_analysis': {
            'avg_total_price': round(sum(prices) / len(prices), 2) if prices else 0,
            'min_total_price': min(prices) if prices else 0,
            'max_total_price': max(prices) if prices else 0,
        },
        'area_analysis': {
            'avg_area': round(sum(areas) / len(areas), 2) if areas else 0,
            'min_area': min(areas) if areas else 0,
            'max_area': max(areas) if areas else 0,
        },
        'price_per_sqm_analysis': {
            'avg_price_per_sqm': round(sum(price_per_sqm) / len(price_per_sqm), 2) if price_per_sqm else 0,
            'min_price_per_sqm': min(price_per_sqm) if price_per_sqm else 0,
            'max_price_per_sqm': max(price_per_sqm) if price_per_sqm else 0,
        }
    }

    return analysis


def save_to_files(properties, analysis):
    """
    保存数据到文件
    """
    # 保存为JSON
    with open('properties.json', 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)

    # 保存为CSV
    df = pd.DataFrame(properties)
    df.to_csv('properties.csv', index=False, encoding='utf-8-sig')

    # 保存分析结果
    with open('analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print("数据已保存到以下文件:")
    print("- properties.json (JSON格式)")
    print("- properties.csv (CSV格式)")
    print("- analysis.json (分析结果)")


def main():
    # 读取HTML文件
    try:
        with open('paste.txt', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("请确保paste.txt文件存在")
        return

    # 解析房源信息
    properties = parse_property_listings(html_content)

    if not properties:
        print("未找到房源信息")
        return

    # 分析数据
    analysis = analyze_properties(properties)

    # 打印结果
    print(f"\n=== 房源信息解析结果 ===")
    print(f"共找到 {len(properties)} 个房源")
    print(f"\n=== 价格分析 ===")
    print(f"平均总价: {analysis['price_analysis']['avg_total_price']}万")
    print(
        f"价格区间: {analysis['price_analysis']['min_total_price']}万 - {analysis['price_analysis']['max_total_price']}万")
    print(f"平均单价: {analysis['price_per_sqm_analysis']['avg_price_per_sqm']}元/㎡")
    print(
        f"单价区间: {analysis['price_per_sqm_analysis']['min_price_per_sqm']}元/㎡ - {analysis['price_per_sqm_analysis']['max_price_per_sqm']}元/㎡")

    print(f"\n=== 面积分析 ===")
    print(f"平均面积: {analysis['area_analysis']['avg_area']}㎡")
    print(f"面积区间: {analysis['area_analysis']['min_area']}㎡ - {analysis['area_analysis']['max_area']}㎡")

    # 显示前3个房源详情
    print(f"\n=== 前3个房源详情 ===")
    for i, prop in enumerate(properties[:3]):
        print(f"\n房源 {i + 1}:")
        print(f"  标题: {prop.get('title', 'N/A')}")
        print(f"  户型: {prop.get('layout', 'N/A')}")
        print(f"  面积: {prop.get('area', 'N/A')}㎡")
        print(f"  朝向: {prop.get('orientation', 'N/A')}")
        print(f"  楼层: {prop.get('floor_info', 'N/A')}")
        print(f"  建造年份: {prop.get('build_year', 'N/A')}")
        print(f"  总价: {prop.get('total_price', 'N/A')}")
        print(f"  单价: {prop.get('price_per_sqm', 'N/A')}")
        print(f"  小区: {prop.get('community', 'N/A')}")
        print(f"  地址: {prop.get('district', '')}{prop.get('area_name', '')}{prop.get('detailed_address', '')}")

    # 保存到文件
    save_to_files(properties, analysis)


if __name__ == "__main__":
    main()