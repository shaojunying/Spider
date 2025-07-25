import os
import json
import logging
import pandas as pd
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List


def setup_logging(log_dir: str = 'logs') -> None:
    """Configure logging settings"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f'bwf_tournament_{datetime.now().strftime("%Y%m%d")}.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_tournament_data(year: str = "2025") -> Dict:
    """
    Fetch tournament data by month for the given year, aggregate and return as a single JSON.
    """
    aggregated_data = []  # This will hold all the game data

    # Iterate over each month of the given year
    for _ in range(0, 1):
        curl_command = f"""
        curl 'https://www.fivb.org/Vis2009/XmlRequest.asmx?Request=%3CRequests%3E%3CRequest%20Type=%22GetBeachTournamentList%22%20Fields=%22Season%20code%20EndDateMainDraw%20StartDateMainDraw%20EndDateQualification%20StartDateQualification%20startDate%20Name%20CountryCode%20City%20Gender%20Type%20OrganizerType%20WebSite%20EventLogos%22%3E%3CFilter%20%20FirstDate=%22{year}-01-01%22%20Statuses=%220%201%206%207%208%209%22/%3E%3C/Request%3E%3C/Requests%3E' \
          -H 'accept: application/json' \
          -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
          -H 'dnt: 1' \
          -H 'origin: https://www.fivb.com' \
          -H 'priority: u=1, i' \
          -H 'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"' \
          -H 'sec-ch-ua-mobile: ?0' \
          -H 'sec-ch-ua-platform: "macOS"' \
          -H 'sec-fetch-dest: empty' \
          -H 'sec-fetch-mode: cors' \
          -H 'sec-fetch-site: cross-site' \
          -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
        """

        try:
            logging.info(f"Fetching tournament data for {year}")
            result = subprocess.run(
                curl_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                response_json = json.loads(result.stdout)
                logging.info(f"Successfully fetched data for {year}")
                aggregated_data.extend(response_json['responses'][0]['data'])  # Aggregate the data
            else:
                logging.error(f"Curl command failed with error: {result.stderr}")
                raise Exception(f"Curl command failed: {result.stderr}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute curl command for {year}: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response for  {year}: {str(e)}")
            raise

    logging.info(f"Successfully aggregated data for {year}. Total games: {len(aggregated_data)}")
    return {"results": aggregated_data}

def safe_get(d, keys, default=''):
    """安全地获取嵌套字典中的值，如果不存在返回默认值。"""
    for key in keys:
        d = d.get(key, {})
        if not d:  # 如果字典为空，返回默认值
            return default
    return d if d else default

def flatten_tournament_data(data: Dict) -> List[Dict]:
    """
    Flatten the nested tournament data structure into a list of tournament entries
    """
    flattened_data = []

    try:
        results = data.get('results', {})
        for event in results:
            if isinstance(event, dict):
                flattened_event = {
                    'Season': event.get('season', ''),
                    'Code': event.get('code', ''),
                    'EndDateMainDraw': event.get('endDateMainDraw', ''),
                    'StartDateMainDraw': event.get('startDateMainDraw', ''),
                    'EndDateQualification': event.get('endDateQualification', ''),
                    'StartDateQualification': event.get('startDateQualification', ''),
                    'StartDate': event.get('startDate', ''),
                    'Name': event.get('name', ''),
                    'CountryCode': event.get('countryCode', ''),
                    'Gender': event.get('gender', ''),
                    'Type': event.get('type', ''),
                    'OrganizerType': event.get('organizerType', ''),
                    'WebSite': event.get('webSite', ''),
                    'EventLogos': event.get('eventLogos', '')
                }
                flattened_data.append(flattened_event)
        logging.info(f"Successfully flattened data for {len(flattened_data)} games")
    except Exception as e:
        logging.error(f"Error flattening tournament data: {str(e)}")
        raise

    return flattened_data


def save_to_excel(data: List[Dict], excel_path: str) -> None:
    """
    Save the tournament data to an Excel file
    """
    try:
        df = pd.DataFrame(data)

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)

        # Save to Excel
        df.to_excel(excel_path, index=False, sheet_name='Tournaments')

        logging.info(f"Successfully saved data to Excel file: {excel_path}")
    except Exception as e:
        logging.error(f"Error saving to Excel: {str(e)}")
        raise

def get_excel_name() -> str:
    filename = os.path.basename(__file__)
    basename = os.path.splitext(filename)[0]
    new_filename = basename + ".xlsx"
    from sport import config
    excel_file_path = os.path.join(config.output_path, new_filename)
    logging.info(f"Saving excel file: {excel_file_path}")
    return str(excel_file_path)

def main():
    setup_logging()
    try:
        logging.info("Starting BWF tournament data processing")

        # Fetch data using curl
        json_data = get_tournament_data()

        # Flatten and process the data
        flattened_data = flatten_tournament_data(json_data)

        # Save to Excel
        save_to_excel(flattened_data, get_excel_name())

        logging.info("BWF tournament data processing completed successfully")

    except Exception as e:
        logging.error(f"Failed to process BWF tournament data: {str(e)}")
        raise


if __name__ == "__main__":
    main()
