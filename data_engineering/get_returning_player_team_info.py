import re
from typing import Any, List, Tuple
import pandas as pd
from tqdm import tqdm

from argparser_config import get_parser
import helper_functions as hf
from constants import SPORTS_REF_STUB, CURRENT_YR


def get_returning_team_stats(team: str, year: int) -> Tuple[float, float]:
    link = f"{SPORTS_REF_STUB}/cbb/schools/{team}/men/{year}.html"
    soup = hf.get_soup(link, rate_limit=True)
    text_div = soup.find("div", {"id": "tfooter_roster"}).text
    decimals = re.findall("\d+\.\d", text_div)
    returning_min_pct = float(decimals[0])
    returning_score_pct = float(decimals[1])
    return (returning_min_pct, returning_score_pct)


def get_all_returning_info(
    year: int = CURRENT_YR,
    output_failures: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    tourney_teams_only = kwargs.get("tourney_teams_only", True)

    # if tourney_teams_only is True, then we only want to get the teams that made the tournament
    all_teams = hf.get_sports_ref_teams(year, tourney_teams_only)

    # list to log teams that failed to get data
    team_info = []
    failed_teams = []
    for team in tqdm(all_teams, desc=f"Getting {year} data"):
        try:
            info = get_returning_team_stats(team, year)
            team_info.append([team, *info])
        except Exception as e:
            # Catch any other errors that occur and log the team's name
            failed_teams.append(team)
    cols = ["team", "returning_min_pct", "returning_score_pct"]
    df = pd.DataFrame(team_info, columns=cols)
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

    table_name = f"returning_player_team_stats{'_tourney' if args.tourney_teams_only else '_all'}"

    if args.dry_run:
        print(
            f"""Running in dry-run mode for {args.year} for 
            {'tourney teams only' if args.tourney_teams_only else 'all teams'}."""
        )
        get_all_returning_info(args.year, args.tourney_teams_only)
        return

    # call the function with the command-line arguments
    df = hf.generate_data_all_years(
        get_all_returning_info,
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
