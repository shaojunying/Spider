import os
import json
import logging
import pandas as pd
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List
from util.log import setup_logging

setup_logging()

def get_tournament_data(year: str = "2025") -> Dict:
    """
    Fetch tournament data by month for the given year, aggregate and return as a single JSON.
    """
    aggregated_data = []  # This will hold all the game data

    # Iterate over each month of the given year
    for month in range(1, 13):
        # Format the month and ensure it's two digits (e.g., "01", "02")
        month_str = f"{month:02d}"

        # Define the start and end dates for the current month
        start_date = f"{year}-{month_str}-01T00:00:00.000Z"
        # Use timedelta to get the last day of the month
        next_month = (datetime(int(year), month, 1) + timedelta(days=32)).replace(day=1)
        end_date = next_month.strftime(f"{year}-%m-01T00:00:00.000Z")

        # Build the curl command
        curl_command = f"""
        curl 'https://digital-api.fiba.basketball/hapi/getgdapgamesbetweentwodates?dateFrom={start_date}&dateTo={end_date}' \
          -H 'Accept: */*' \
          -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6,und;q=0.5' \
          -H 'Connection: keep-alive' \
          -H 'DNT: 1' \
          -H 'Origin: https://www.fiba.basketball' \
          -H 'Referer: https://www.fiba.basketball/' \
          -H 'Sec-Fetch-Dest: empty' \
          -H 'Sec-Fetch-Mode: cors' \
          -H 'Sec-Fetch-Site: same-site' \
          -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36' \
          -H 'content-type: application/json' \
          -H 'ocp-apim-subscription-key: c7616771331d48dd9262fa001b4c10be' \
          -H 'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"' \
          -H 'sec-ch-ua-mobile: ?0' \
          -H 'sec-ch-ua-platform: "macOS"'
        """

        try:
            logging.info(f"Fetching tournament data for {year}-{month_str}")
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
                logging.info(f"Successfully fetched data for {year}-{month_str}")
                aggregated_data.extend(response_json)  # Aggregate the data
            else:
                logging.error(f"Curl command failed with error: {result.stderr}")
                raise Exception(f"Curl command failed: {result.stderr}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute curl command for {year}-{month_str}: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response for {year}-{month_str}: {str(e)}")
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
        for game in results:
            if isinstance(game, dict):
                if isinstance(game, dict):
                    flattened_game = {
                        'Game ID': game.get('gameId', ''),
                        'Game Name': game.get('gameName', ''),
                        'Game Number': game.get('gameNumber', ''),
                        'Status Code': game.get('statusCode', ''),
                        'Team A ID': safe_get(game, ['teamA', 'teamId']),
                        'Team A Organisation ID': safe_get(game, ['teamA', 'organisationId']),
                        'Team A Code': safe_get(game, ['teamA', 'code']),
                        'Team A Official Name': safe_get(game, ['teamA', 'officialName']),
                        'Team A Short Name': safe_get(game, ['teamA', 'shortName']),
                        'Team B ID': safe_get(game, ['teamB', 'teamId']),
                        'Team B Organisation ID': safe_get(game, ['teamB', 'organisationId']),
                        'Team B Code': safe_get(game, ['teamB', 'code']),
                        'Team B Official Name': safe_get(game, ['teamB', 'officialName']),
                        'Team B Short Name': safe_get(game, ['teamB', 'shortName']),
                        'Team A Score': game.get('teamAScore', ''),
                        'Team B Score': game.get('teamBScore', ''),
                        'Is Live': game.get('isLive', ''),
                        'Current Period': game.get('currentPeriod', ''),
                        'Chrono': game.get('chrono', ''),
                        'Live Game Status': game.get('liveGameStatus', ''),
                        'Current Period Status': game.get('currentPeriodStatus', ''),
                        'Host City': game.get('hostCity', ''),
                        'Host Country': game.get('hostCountry', ''),
                        'Host Country Code': game.get('hostCountryCode', ''),
                        'Venue ID': game.get('venueId', ''),
                        'Venue Name': game.get('venueName', ''),
                        'Game Date Time': game.get('gameDateTime', ''),
                        'Game Date Time UTC': game.get('gameDateTimeUTC', ''),
                        'Has Time Game Date Time': game.get('hasTimeGameDateTime', ''),
                        'IANA Time Zone': game.get('ianaTimeZone', ''),
                        'UTC Offset': game.get('utcOffset', ''),
                        'Is Postponed': game.get('isPostponed', ''),
                        'Is Played Behind Closed Doors': game.get('isPlayedBehindClosedDoors', ''),
                        'Venue Capacity': game.get('venueCapacity', ''),
                        'Spectators': game.get('spectators', ''),
                        'Statistic System': game.get('statisticSystem', ''),
                        'Group ID': game.get('groupId', ''),
                        'Group Pairing Code': game.get('groupPairingCode', ''),
                        'Round ID': safe_get(game, ['round', 'roundId']),
                        'Round Code': safe_get(game, ['round', 'roundCode']),
                        'Round Name': safe_get(game, ['round', 'roundName']),
                        'Round Number': safe_get(game, ['round', 'roundNumber']),
                        'Round Type': safe_get(game, ['round', 'roundType']),
                        'Round Status Code': safe_get(game, ['round', 'roundStatusCode']),
                        'Competition ID': safe_get(game, ['competition', 'competitionId']),
                        'Competition Code': safe_get(game, ['competition', 'competitionCode']),
                        'Competition Official Name': safe_get(game, ['competition', 'officialName']),
                        'Competition Start': safe_get(game, ['competition', 'start']),
                        'Competition End': safe_get(game, ['competition', 'end']),
                        'Competition Status': safe_get(game, ['competition', 'status']),
                        'Competition Age Category': safe_get(game, ['competition', 'ageCategory']),
                        'Competition Gender': safe_get(game, ['competition', 'gender']),
                        'Competition FIBA Zone': safe_get(game, ['competition', 'fibaZone']),
                        'Competition Zone Code': safe_get(game, ['competition', 'zoneInformation', 'zoneCode']),
                        'Competition Type': safe_get(game, ['competition', 'competitionType']),
                        'Competition Category Code': safe_get(game, ['competition', 'competitionCategory', 'code']),
                        'Competition Category Name': safe_get(game, ['competition', 'competitionCategory', 'name'])
                    }
                    if 'CHN' == flattened_game['Host Country Code']:
                        logging.info("Game in China: " + str(flattened_game))
                        flattened_data.append(flattened_game)
                    else:
                        logging.info("Game not in China: " + str(flattened_game))

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
