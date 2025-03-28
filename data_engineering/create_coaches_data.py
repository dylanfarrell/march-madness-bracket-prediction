import pandas as pd

import helper_functions as hf
from argparser_config import get_parser
from constants import SPORTS_REF_STUB, MODE_DIRECTORY


def create_coaches_data(year: int, mode: str) -> pd.DataFrame:
    mode = MODE_DIRECTORY[mode]
    # Sports Reference uses "men" and "women" instead of the plural, so we lop off the "s"
    link = f"{SPORTS_REF_STUB}/cbb/seasons/{mode[:-1]}/{year}-coaches.html"
    soup = hf.get_soup(link, rate_limit=True)
    coach_table = soup.find("table", {"id": "coaches"})
    coach_rows = coach_table.find("tbody").find_all("tr")

    coach_data = []

    for i, row in enumerate(coach_rows):
        # non-data rows have class = "over_header" or "thead"
        # data rows have no class attribtue and return None
        if row.get("class") is None:
            try:
                coach_name = row.find("th", {"data-stat": "coach"}).text
                team = row.find("td", {"data-stat": "school"}).a["href"].split("/")[3]
                team_name = row.find("td", {"data-stat": "school"}).text
                coach_since = row.find("td", {"data-stat": "since"}).text
                ap_pre = row.find("td", {"data-stat": "ap_pre"}).text
                is_ap_pre_top_5 = False if ap_pre == "" else int(ap_pre) <= 5
                is_ap_pre_top_15 = False if ap_pre == "" else int(ap_pre) <= 15
                is_ap_pre_top_25 = False if ap_pre == "" else int(ap_pre) <= 25

                wins_cur = int(row.find("td", {"data-stat": "wins_cur"}).text)
                losses_cur = int(row.find("td", {"data-stat": "losses_cur"}).text)
                games_cur = wins_cur + losses_cur
                coach_wl_cur = row.find("td", {"data-stat": "wl_pct_cur"}).text

                wins_car = int(row.find("td", {"data-stat": "wins_car"}).text)
                losses_car = int(row.find("td", {"data-stat": "losses_car"}).text)
                games_car = wins_car + losses_car
                coach_wl_car = row.find("td", {"data-stat": "wl_pct_car"}).text

                tourneys_car = row.find("td", {"data-stat": "ncaa_car"}).text
                sw16_car = row.find("td", {"data-stat": "sw16_car"}).text
                ff_car = row.find("td", {"data-stat": "ff_car"}).text
                champ_car = row.find("td", {"data-stat": "champ_car"}).text

                new_row = [
                    year,
                    team,
                    coach_name,
                    team_name,
                    coach_since,
                    is_ap_pre_top_5,
                    is_ap_pre_top_15,
                    is_ap_pre_top_25,
                    wins_cur,
                    losses_cur,
                    games_cur,
                    coalesce_empty_string_and_cast(coach_wl_cur, float),
                    wins_car,
                    losses_car,
                    games_car,
                    coalesce_empty_string_and_cast(coach_wl_car, float),
                    coalesce_empty_string_and_cast(tourneys_car, int),
                    coalesce_empty_string_and_cast(sw16_car, int),
                    coalesce_empty_string_and_cast(ff_car, int),
                    coalesce_empty_string_and_cast(champ_car, int),
                ]
                coach_data.append(new_row)
            except:
                print(f"Skipping bad data: year {year}, row {i}.")
    coach_df = pd.DataFrame(
        coach_data,
        columns=[
            "year",
            "team",
            "coach_name",
            "team_name",
            "coach_since",
            "is_ap_pre_top_5",
            "is_ap_pre_top_15",
            "is_ap_pre_top_25",
            "wins_cur",
            "losses_cur",
            "games_cur",
            "coach_wl_cur",
            "wins_car",
            "losses_car",
            "games_car",
            "coach_wl_car",
            "tourneys_car",
            "sw16_car",
            "ff_car",
            "champ_car",
        ],
    )
    coach_df_deduped = dedupe_coaches_data(coach_df)
    return coach_df_deduped


# coalesce empty string to 0
def coalesce_empty_string_and_cast(value: str, cast_type) -> int:
    return 0 if value == "" else cast_type(value)


def dedupe_coaches_data(df: pd.DataFrame) -> pd.DataFrame:
    # dedupe the data, keeping the most recent coach for each team
    # if there is a tie (multiple coaches started coaching in the same year), keep the coach with
    # the highest win percentage
    df_sorted = df.sort_values(
        by=["year", "team", "coach_since", "games_cur"],
        ascending=[True, True, False, False],
    )

    df_deduped = df_sorted.drop_duplicates(
        subset=["year", "team"], keep="first"
    ).reset_index(drop=True)

    year = df["year"].iloc[0]
    print(f"{year}: Dropped {len(df) - len(df_deduped)} duplicate team rows.")

    return df_deduped


def main():
    # parse the command-line arguments
    parser = get_parser()
    args = parser.parse_args()

    table_name = "coaches_data"

    if args.dry_run:
        print(f"Running in dry-run mode for {args.year}.")
        create_coaches_data(args.year, args.mode)
        return

    # call the function with the command-line arguments
    df = hf.generate_data_all_years(
        create_coaches_data,
        year=args.year,
        mode=args.mode,
        recompute=args.recompute,
        table_name=table_name,
    )

    # write the dataframe to a csv
    file_path = f"{hf.get_generated_dir(args.year, args.mode)}/{table_name}.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
