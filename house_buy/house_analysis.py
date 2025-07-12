import pandas as pd
from typing import List, Dict, Set


def color_text(text: str, color: str) -> str:
    """添加终端颜色"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"


def get_detail(ids: Set[str], detail_df: pd.DataFrame) -> pd.DataFrame:
    """获取指定id的详情信息"""
    if not ids:
        return pd.DataFrame(columns=detail_df.columns)
    return detail_df[detail_df['id'].isin(ids)]


def print_house_list(title: str, ids: Set[str], detail_df: pd.DataFrame, output_detail: bool):
    print(f"\n{title} {len(ids)} 套")
    if output_detail and ids:
        display_df = get_detail(ids, detail_df)
        if not display_df.empty:
            print(display_df[['id', '小区', '户型', '建筑面积', '楼层', '朝向', '装修', '单价']])


def print_price_changes(price_changed_ids: List[str],
                        df_yesterday: pd.DataFrame,
                        df_today: pd.DataFrame,
                        detail_df: pd.DataFrame,
                        output_detail: bool):
    print(f"\n🔁 价格变化房源 {len(price_changed_ids)} 套")
    if not output_detail or not price_changed_ids:
        return

    display_df = get_detail(price_changed_ids, detail_df)
    for hid in price_changed_ids:
        old_price = float(df_yesterday.loc[hid, '单价'])
        new_price = float(df_today.loc[hid, '单价'])

        row = display_df[display_df['id'] == hid]
        if row.empty:
            print(f"{hid} | 价格 {old_price} ➡️ {new_price}")
            continue

        info = row.iloc[0]
        area = float(info['建筑面积'])

        old_total = round(old_price * area / 10000, 2)
        new_total = round(new_price * area / 10000, 2)

        arrow = "🔺" if new_price > old_price else "🔻"
        color = "red" if new_price > old_price else "green"

        price_str = color_text(f"{old_price} ➡️ {new_price} 元/㎡", color)
        total_str = color_text(f"{old_total} ➡️ {new_total} 万元", color)

        print(f"{arrow} {info['id']} | {info['小区']} | {info['户型']} | {area}㎡ | {info['楼层']} | "
              f"{price_str} | 总价：{total_str}")


def print_price_drop_rank(detail_df: pd.DataFrame, top_n: int = None):
    """打印房源按 最高价→最低价 的降幅排序结果（含总价变化、单价变化、日期）"""
    df = detail_df.copy()
    df['最高价'] = pd.to_numeric(df['最高价'], errors='coerce')
    df['最低价'] = pd.to_numeric(df['最低价'], errors='coerce')
    df['降幅'] = df['最高价'] - df['最低价']
    df = df[df['降幅'] > 0].copy()
    df_sorted = df.sort_values(by='降幅', ascending=False)

    if top_n:
        df_sorted = df_sorted.head(top_n)

    print("\n📉 房价降幅排名（最高价 -> 最低价）:\n")

    # 表头
    header = (
        f"{'箭头':<2} {'ID':<20} {'小区':<12} {'户型':<8} {'面积':<8} {'楼层':<10} "
        f"{'单价变动':<25} {'总价变动':<28} {'降幅':<10} {'最高价日':<10} {'最低价日':<10}"
    )
    print(header)
    print("-" * len(header))

    for _, row in df_sorted.iterrows():
        try:
            id_ = str(row['id'])
            name = str(row['小区'])[:12]
            layout = str(row['户型'])
            area = float(row['建筑面积'])
            area_str = f"{area:.2f}㎡"
            floor = str(row['楼层'])

            # 单价变动
            high_price = float(row['最高价'])
            low_price = float(row['最低价'])
            diff = high_price - low_price
            price_str = f"{int(high_price)} ➡️ {int(low_price)} 元/㎡"
            drop_str = f"{int(diff)} 元"

            # 总价变动
            high_total = round(high_price * area / 10000, 2)
            low_total = round(low_price * area / 10000, 2)
            total_price_str = f"{high_total:.1f} ➡️ {low_total:.1f} 万元"

            # 日期
            high_date = str(row['最高价日期'])[:10]
            low_date = str(row['最低价日期'])[:10]

            # 输出
            print(f"{'🔻':<2} {id_:<20} {name:<12} {layout:<8} {area_str:<8} {floor:<10} "
                  f"{price_str:<25} {total_price_str:<28} {drop_str:<10} {high_date:<10} {low_date:<10}")
        except Exception as e:
            print(f"[跳过异常行] id={row.get('id', 'N/A')} error={e}")


def print_daily_average_price_trend(history_df: pd.DataFrame):
    """
    打印每一天的房源均价变化趋势
    """
    avg_price_df = history_df.groupby('日期')['单价'].mean().reset_index()
    print("\n📈 每日均价趋势（元/㎡）:")
    for _, row in avg_price_df.iterrows():
        date_str = row['日期'].date()
        avg_price = row['单价']
        print(f"{date_str} : {avg_price:.2f} 元/㎡")


def print_top_bottom_price_by_community(detail_df: pd.DataFrame, top_n: int = 3):
    """
    统计并打印每个小区单价最高的top_n和最低的top_n房源
    """
    print("\n🏆 各小区单价最高和最低房源排名：")
    for community, group in detail_df.groupby('小区'):
        group_sorted = group.copy()
        group_sorted['单价'] = pd.to_numeric(group_sorted['单价'], errors='coerce')

        top_list = group_sorted.nlargest(top_n, '单价')
        bottom_list = group_sorted.nsmallest(top_n, '单价')

        print(f"\n小区：{community}")
        print(f"  🔺 最高单价前 {top_n} 套：")
        for _, row in top_list.iterrows():
            print(f"    ID: {row['id']}, 单价: {row['单价']} 元/㎡, 户型: {row['户型']}, 面积: {row['建筑面积']}㎡, 楼层: {row['楼层']}")

        print(f"  🔻 最低单价前 {top_n} 套：")
        for _, row in bottom_list.iterrows():
            print(f"    ID: {row['id']}, 单价: {row['单价']} 元/㎡, 户型: {row['户型']}, 面积: {row['建筑面积']}㎡, 楼层: {row['楼层']}")




def analyze_house_changes(price_history_path: str,
                          house_info_path: str,
                          output_detail: bool = True,
                          latest_only: bool = False,
                          show_drop_rank: bool = False,
                          top_n: int = None) -> List[Dict]:
    history_df = pd.read_csv(price_history_path, dtype={'id': str})
    detail_df = pd.read_csv(house_info_path, dtype={'id': str})

    history_df['日期'] = pd.to_datetime(history_df['日期'])
    grouped = history_df.groupby('日期')
    dates = sorted(grouped.groups.keys())

    results = []

    range_to_process = range(len(dates) - 1, len(dates)) if latest_only else range(1, len(dates))

    for i in range_to_process:
        today, yesterday = dates[i], dates[i - 1]
        df_today = grouped.get_group(today).set_index('id')
        df_yesterday = grouped.get_group(yesterday).set_index('id')

        today_ids = set(df_today.index)
        yesterday_ids = set(df_yesterday.index)

        added_ids = today_ids - yesterday_ids
        removed_ids = yesterday_ids - today_ids
        common_ids = today_ids & yesterday_ids

        price_changed_ids = [
            hid for hid in common_ids
            if df_today.loc[hid, '单价'] != df_yesterday.loc[hid, '单价']
        ]

        # 所有相关id，准备详情
        involved_ids = added_ids | removed_ids | set(price_changed_ids)
        involved_detail = detail_df[detail_df['id'].isin(involved_ids)]

        # 按小区分组
        for community, group in involved_detail.groupby('小区'):
            comm_ids = set(group['id'])

            comm_added = added_ids & comm_ids
            comm_removed = removed_ids & comm_ids
            comm_price_changed = [hid for hid in price_changed_ids if hid in comm_ids]

            print(f"\n📅 日期：{today.date()}（小区：{community}）")
            print_house_list("🟢 新增房源", comm_added, detail_df, output_detail)
            print_house_list("🔴 下架房源", comm_removed, detail_df, output_detail)
            print_price_changes(comm_price_changed, df_yesterday, df_today, detail_df, output_detail)

            results.append({
                '日期': today.date(),
                '小区': community,
                '新增': len(comm_added),
                '下架': len(comm_removed),
                '价格变动': len(comm_price_changed),
            })

    # 计算每日各小区均价趋势
    print("\n📈 各小区每日均价趋势（元/㎡）:")
    avg_prices = history_df.groupby(['日期', '小区'])['单价'].mean().reset_index()
    for community, group in avg_prices.groupby('小区'):
        print(f"\n小区：{community}")
        for _, row in group.iterrows():
            print(f"{row['日期'].date()} : {row['单价']:.2f} 元/㎡")

    # 分小区输出降幅排行
    if show_drop_rank:
        print("\n📉 各小区房价降幅排名（最高价 -> 最低价）:")
        for community, group in detail_df.groupby('小区'):
            print(f"\n小区：{community}")
            print_price_drop_rank(group, top_n)

    # 新增调用：打印每个小区单价最高和最低房源
    print_top_bottom_price_by_community(detail_df, top_n=3)

    return results

if __name__ == '__main__':
    import argparse
    from config import DEFAULT_HISTORY_PATH, DEFAULT_INFO_PATH

    parser = argparse.ArgumentParser(description="每日房源变化分析")
    parser.add_argument('--history', default=DEFAULT_HISTORY_PATH, help='price_history.csv 文件路径')
    parser.add_argument('--info', default=DEFAULT_INFO_PATH, help='houses_info.csv 文件路径')
    parser.add_argument('--brief', action='store_true', help='只显示统计摘要（不输出详情）')
    parser.add_argument('--latest', action='store_true', help='只分析最近一天的变化')
    parser.add_argument('--drop-rank', action='store_true', default=True, help='是否显示降幅从大到小的房源')
    parser.add_argument('--top', type=int, help='只显示降幅前 N 套')

    args = parser.parse_args()

    analyze_house_changes(
        price_history_path=args.history,
        house_info_path=args.info,
        output_detail=not args.brief,
        latest_only=args.latest,
        show_drop_rank=args.drop_rank,
        top_n=args.top
    )
