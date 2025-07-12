import os
import json
import logging
import pandas as pd
import subprocess
from datetime import datetime
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
    Execute curl command to fetch tournament data
    """
    curl_command = f"""
    curl 'https://extranet-lv.bwfbadminton.com/api/vue-cal-event-tournaments' \
      -H 'accept: application/json, text/plain, */*' \
      -H 'accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
      -H 'authorization: Bearer 2|NaXRu9JnMpSdb8l86BkJxj6gzKJofnhmExwr8EWkQtHoattDAGimsSYhpM22a61e1crjTjfIGTKfhzxA' \
      -H 'content-type: application/json;charset=UTF-8' \
      -H 'dnt: 1' \
      -H 'origin: https://bwfbadminton.com' \
      -H 'priority: u=1, i' \
      -H 'referer: https://bwfbadminton.com/' \
      -H 'sec-ch-ua: "Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: "macOS"' \
      -H 'sec-fetch-dest: empty' \
      -H 'sec-fetch-mode: cors' \
      -H 'sec-fetch-site: same-site' \
      -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36' \
      --data-raw '{{"yearKey":"{year}","smallBackground":true}}'
    """

    try:
        logging.info(f"Fetching tournament data for year {year}")
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
            logging.info("Successfully fetched tournament data")
            return response_json
        else:
            logging.error(f"Curl command failed with error: {result.stderr}")
            raise Exception(f"Curl command failed: {result.stderr}")

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to execute curl command: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {str(e)}")
        raise


def flatten_tournament_data(data: Dict) -> List[Dict]:
    """
    Flatten the nested tournament data structure into a list of tournament entries
    """
    flattened_data = []

    try:
        results = data.get('results', {})
        for month in results:
            monthly_data = results[month]
            if isinstance(monthly_data, dict):
                for tournament in monthly_data.values():
                    if isinstance(tournament, dict):
                        tournament_info = {
                            'Month': month,
                            'Name': tournament.get('name', ''),
                            'Start Date': tournament.get('start_date', ''),
                            'End Date': tournament.get('end_date', ''),
                            'Location': tournament.get('location', ''),
                            'Progress': tournament.get('progress', ''),
                            'Tournament URL': tournament.get('url', ''),
                            'Logo URL': tournament.get('logo', ''),
                            'Header URL': tournament.get('header_url', '')
                        }
                        flattened_data.append(tournament_info)

        logging.info(f"Successfully flattened data for {len(flattened_data)} tournaments")
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

        # Convert datetime strings to datetime objects
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['End Date'] = pd.to_datetime(df['End Date'])

        # Sort by start date
        df = df.sort_values('Start Date')

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)

        # Save to Excel
        df.to_excel(excel_path, index=False, sheet_name='Tournaments')

        logging.info(f"Successfully saved data to Excel file: {excel_path}")
    except Exception as e:
        logging.error(f"Error saving to Excel: {str(e)}")
        raise


def main():
    """Main function to process tournament data and save to Excel"""
    # Setup logging
    setup_logging()

    try:
        # Generate filename as per requirements
        filename = os.path.basename(__file__)
        basename = os.path.splitext(filename)[0]
        new_filename = basename + ".xlsx"
        from sport import config
        excel_file_path = os.path.join(config.output_path, new_filename)

        logging.info("Starting BWF tournament data processing")

        # Fetch data using curl
        json_data = get_tournament_data()

        # Flatten and process the data
        flattened_data = flatten_tournament_data(json_data)

        # Save to Excel
        save_to_excel(flattened_data, excel_file_path)

        logging.info("BWF tournament data processing completed successfully")

    except Exception as e:
        logging.error(f"Failed to process BWF tournament data: {str(e)}")
        raise


if __name__ == "__main__":
    main()