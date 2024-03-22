import pandas as pd
from typing import Any, Tuple

from bs4 import BeautifulSoup
from tqdm import tqdm

import helper_functions as hf
from argparser_config import get_parser
from constants import SPORTS_REF_STUB, CURRENT_YR

YR_TO_NUM = {"FR": 1, "SO": 2, "JR": 3, "SR": 4}


def get_player_id(row, tag_type: str) -> str:
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


def get_player_info(soup: BeautifulSoup) -> pd.DataFrame:
    # Find the table by ID or class
    table = soup.find("table", {"id": "roster"})

    # Lists to store extracted data
    player_ids = []
    class_years_lst = []
    heights_inches_lst = []
    lbs_lst = []
    hometowns_lst = []
    last_names_lst = []

    # Iterate through each row in the table body
    for row in table.find_all("tr")[1:]:  # Skipping the header row
        player_id = get_player_id(row, "th")

        class_year_str = row.find("td", {"data-stat": "class"}).text
        # return None in the rare case it's not in the dictionary
        class_year = YR_TO_NUM.get(class_year_str, None)
        height = row.find("td", {"data-stat": "height"}).text
        height_inches = convert_height_to_inches(height)
        lbs_str = row.find("td", {"data-stat": "weight"}).text
        lbs = try_cast(lbs_str, float, None)
        hometown = row.find("td", {"data-stat": "hometown"}).text
        last_name = (
            row.find("th", {"data-stat": "player"}).find("a").text.split(" ")[-1]
        )

        player_ids.append(player_id)
        class_years_lst.append(class_year)
        heights_inches_lst.append(height_inches)
        lbs_lst.append(lbs)
        hometowns_lst.append(hometown)
        last_names_lst.append(last_name)

    # Create a DataFrame
    df_info = pd.DataFrame(
        {
            "player_id": player_ids,
            "class_year": class_years_lst,
            "height": heights_inches_lst,
            "weight": lbs_lst,
            "hometown": hometowns_lst,
            "last_name": last_names_lst,
        }
    )

    return df_info


def get_minutes_played(soup: BeautifulSoup) -> pd.DataFrame:
    # Find the table by ID or class
    table = soup.find("table", {"id": "per_game"})

    # Lists to store extracted data
    player_ids = []
    minutes_played = []

    # Iterate through each row in the table body
    for row in table.find_all("tr")[1:]:  # Skipping the header row
        # Extract player's unique part of the URL and MP
        player_id = get_player_id(row, "td")
        mp_str = row.find("td", {"data-stat": "mp_per_g"}).text
        mp = hf.try_cast(mp_str, float, None)

        player_ids.append(player_id)
        minutes_played.append(mp)

    # Create a DataFrame
    df_minutes = pd.DataFrame({"player_id": player_ids, "min_per_game": minutes_played})

    return df_minutes


def get_minute_weighted_avg(df: pd.DataFrame, col: str) -> float:
    return sum([m * h for m, h in zip(df[col], df["min_per_game"])]) / sum(
        df["min_per_game"]
    )


def get_team_info(team: str, year: int = CURRENT_YR) -> Tuple[float, float, float]:
    link = f"{SPORTS_REF_STUB}/cbb/schools/{team}/men/{year}.html"
    soup = hf.get_soup(link, rate_limit=True)
    df_info = get_player_info(soup)
    df_min = get_minutes_played(soup)
    df_joined = df_info.merge(df_min)
    # comfortable dropping data here -- assumption is that data is MNAR
    df_joined.dropna(inplace=True)
    avg_yr = get_minute_weighted_avg(df_joined, "class_year")
    avg_height = get_minute_weighted_avg(df_joined, "height")
    avg_weight = get_minute_weighted_avg(df_joined, "weight")
    return (avg_yr, avg_height, avg_weight)


def get_all_team_info(
    year: int = CURRENT_YR,
    output_failures: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    tourney_teams_only = kwargs.get("tourney_teams_only", True)

    # if tourney_teams_only is True, then we only want to get the teams that made the tournament
    all_teams = hf.get_sports_ref_teams(year, tourney_teams_only)

    team_info = []
    failed_teams = []
    for team in tqdm(all_teams, desc=f"Getting {year} data"):
        try:
            info = get_team_info(team, year)
            team_info.append([team, *info])
        except Exception as e:
            # Catch any other errors that occur and log the team's name
            failed_teams.append(team)
    df = pd.DataFrame(team_info, columns=["team", "avg_yr", "avg_height", "avg_weight"])
    df["year"] = year

    if output_failures:
        print(f"The following teams failed to get data: {failed_teams}")

    return df


def main():
    # Parse the command-line arguments
    parser = get_parser()
    parser.add_argument(
        "--tourney_teams_only",
        action="store_true",
        help="Whether to loop through all teams or only teams that made the tournament. Defaults to False.",
        default=False,
    )
    args = parser.parse_args()

    table_name = (
        f"team_weighted_info{'_tourney' if args.tourney_teams_only else '_all'}"
    )

    if args.dry_run:
        print(
            f"""Running in dry-run mode for {args.year} for 
            {'tourney teams only' if args.tourney_teams_only else 'all teams'}."""
        )
        get_all_team_info(args.year, args.tourney_teams_only)
        return

    # call the function with the command-line arguments
    df = hf.generate_data_all_years(
        get_all_team_info,
        year=args.year,
        recompute=args.recompute,
        tourney_teams_only=args.tourney_teams_only,
        table_name=table_name,
    )

    # write the dataframe to a csv
    file_path = f"{hf.get_generated_dir(args.year)}/{table_name}.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
