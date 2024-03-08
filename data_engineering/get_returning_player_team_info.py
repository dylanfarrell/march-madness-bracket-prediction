import re
import pandas as pd
from tqdm import tqdm

from argparser_config import get_parsed_args
import helper_functions as hf
from constants import SPORTS_REF_STUB, CURRENT_YR


def get_returning_team_stats(team):
    link = f"{SPORTS_REF_STUB}/cbb/schools/{team}/men/2024.html"
    soup = hf.get_soup(link, rate_limit=True)
    text_div = soup.find("div", {"id": "tfooter_roster"}).text
    decimals = re.findall("\d+\.\d", text_div)
    returning_min_pct = float(decimals[0])
    returning_score_pct = float(decimals[1])
    return (returning_min_pct, returning_score_pct)


def get_all_returning_info(teams, year=CURRENT_YR, overwrite=False) -> list[str]:
    # list to log teams that failed to get data
    failed_teams = []

    team_info = []
    for team in tqdm(teams, desc="Iterating throughs all teams:"):
        try:
            info = get_returning_team_stats(team)
            team_info.append([team, *info])
        except Exception as e:
            # Catch any other errors that occur and log the team's name
            failed_teams.append(team)
    cols = ["team", "returning_min_pct", "returning_score_pct"]
    df = pd.DataFrame(team_info, columns=cols)
    return df, failed_teams


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

    # Call the function with the command-line arguments
    df = get_all_returning_info(yr=args.year)

    file_path = f"{hf.get_generated_dir(args.year)}/returning_player_team_stats.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
