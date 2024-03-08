import time
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from constants import SPORTS_REF_STUB, CURRENT_YR
from argparser_config import get_parsed_args
import helper_functions as hf
from tqdm import tqdm

YR_TO_NUM = {"FR": 1, "SO": 2, "JR": 3, "SR": 4}


def get_player_id(row, tag_type):
    player_link = row.find(tag_type, {"data-stat": "player"}).find("a")["href"]
    player_id = player_link.split("/")[-1].replace(".html", "")
    return player_id


# Function to convert height from ft-in to inches
def convert_height_to_inches(height: str) -> int | None:
    parts = height.split("-")
    if len(parts) == 2:
        feet, inches = parts
        return int(feet) * 12 + float(inches)
    return None


def get_height_and_year(soup):
    # Find the table by ID or class
    table = soup.find("table", {"id": "roster"})

    # Lists to store extracted data
    player_ids = []
    years = []
    heights_inches = []

    # Iterate through each row in the table body
    for row in table.find_all("tr")[1:]:  # Skipping the header row
        player_id = get_player_id(row, "th")

        yr_str = row.find("td", {"data-stat": "class"}).text
        # return None in the rare case it's not in the dictionary
        year = YR_TO_NUM.get(yr_str, None)
        height = row.find("td", {"data-stat": "height"}).text
        height_inches = convert_height_to_inches(height)

        player_ids.append(player_id)
        years.append(year)
        heights_inches.append(height_inches)

    # Create a DataFrame
    df_info = pd.DataFrame(
        {"player_id": player_ids, "year": years, "height": heights_inches}
    )

    return df_info


def get_minutes_played(soup):
    # Find the table by ID or class
    table = soup.find("table", {"id": "per_game"})

    # Lists to store extracted data
    player_ids = []
    minutes_played = []

    # Iterate through each row in the table body
    for row in table.find_all("tr")[1:]:  # Skipping the header row
        # Extract player's unique part of the URL and MP
        player_id = get_player_id(row, "td")
        mp = float(row.find("td", {"data-stat": "mp_per_g"}).text)

        player_ids.append(player_id)
        minutes_played.append(mp)

    # Create a DataFrame
    df_minutes = pd.DataFrame({"player_id": player_ids, "min_per_game": minutes_played})

    return df_minutes


def get_minute_weighted_avg(df, col):
    return sum([m * h for m, h in zip(df[col], df["min_per_game"])]) / sum(
        df["min_per_game"]
    )


def get_team_info(team, year=CURRENT_YR):
    link = f"{SPORTS_REF_STUB}/cbb/schools/{team}/men/{year}.html"
    soup = hf.get_soup(link, rate_limit=True)
    df_info = get_height_and_year(soup)
    df_min = get_minutes_played(soup)
    df_joined = df_info.merge(df_min)
    # comfortable dropping data here -- assumption is that data is MNAR
    df_joined.dropna(inplace=True)
    avg_yr = get_minute_weighted_avg(df_joined, "year")
    avg_height = get_minute_weighted_avg(df_joined, "height")
    return avg_yr, avg_height


def get_all_team_info(teams, year=CURRENT_YR, output_failures=True) -> pd.DataFrame:
    team_info = []
    failed_teams = []
    for team in tqdm(teams, desc="Getting team info"):
        try:
            info = get_team_info(team, year)
            team_info.append([team, *info])
        except Exception as e:
            # Catch any other errors that occur and log the team's name
            failed_teams.append(team)
    df = pd.DataFrame(team_info, columns=["team", "avg_yr", "avg_height"])

    if output_failures:
        print(f"The following teams failed to get data: {failed_teams}")

    return df


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

    all_teams = hf.get_all_sports_ref_teams(year=args.year)
    df = get_all_team_info(all_teams, year=args.year)
    file_path = f"{hf.get_generated_dir(args.year)}/team_weighted_info.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
