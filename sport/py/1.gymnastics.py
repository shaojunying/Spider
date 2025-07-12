import os

import pandas as pd
import requests

from sport import config


def fetch_gymnastics_events():
    url = 'https://www.gymnastics.sport/api/sportevents/'

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5',
        'dnt': '1',
        'referer': 'https://www.gymnastics.sport/site/events/search.php?type=sport',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    params = {
        'from': '2025-01-01',
        'to': '2025-12-31',
        'level': '',
        'discipline': '',
        'ageGroupType': '',
        'country': '',
        'title': '',
        'id': '',
        'status': ''
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def process_data(data):
    events = data['data']
    processed_data = []

    for event in events:
        # Convert disciplines list to comma-separated string
        disciplines = ', '.join([d['code'] for d in event['disciplines']])

        processed_event = {
            'ID': event['id'],
            'Title': event['title'],
            'Start Date': event['startevent'],
            'End Date': event['endevent'],
            'City': event['city']['name'],
            'Country': event['city']['country']['code'],
            'Status': event['status'],
            'Disciplines': disciplines,
            'Has Results': event['hasresults']
        }
        processed_data.append(processed_event)

    return pd.DataFrame(processed_data)


def save_to_excel(df, filename):
    # Sort by start date
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df = df.sort_values('Start Date')

    # Convert back to string format for Excel
    df['Start Date'] = df['Start Date'].dt.strftime('%Y-%m-%d')

    # Create Excel writer with xlsxwriter engine
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Events')

        # Auto-adjust columns width
        worksheet = writer.sheets['Events']
        for idx, col in enumerate(df.columns):
            series = df[col]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(col))
            ) + 1
            worksheet.set_column(idx, idx, max_len)


def main():
    # Fetch data
    print("Fetching data from gymnastics.sport...")
    data = fetch_gymnastics_events()

    # Process data
    print("Processing data...")
    df = process_data(data)

    filename = os.path.basename(__file__)
    basename = os.path.splitext(filename)[0]
    new_filename = basename + ".xlsx"
    excel_file_path = os.path.join(config.output_path, new_filename)
    save_to_excel(df, excel_file_path)

    print(f"Done! Saved {len(df)} events to {excel_file_path}")


if __name__ == "__main__":
    main()