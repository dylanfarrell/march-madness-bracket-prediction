import pandas as pd

import helper_functions as hf
from argparser_config import get_parser
from constants import SPORTS_REF_STUB


def create_team_stats(year: int) -> pd.DataFrame:
    link = f"{SPORTS_REF_STUB}/cbb/seasons/men/{year}-school-stats.html"
    soup = hf.get_soup(link)

    teams_data = []

    table_body = soup.find("tbody")

    # Find all rows in the table body
    rows = table_body.find_all("tr")
    for row in rows:
        # non-data rows have class = "over_header" or "thead"
        # data rows have no class attribtue and return None
        if row.get("class") is None:
            row_data = {}
            # Extracting School Name and ID
            team_tag = row.find("a")
            if team_tag:
                team = team_tag["href"].split("/")[3]  # Extract school ID
                row_data["team"] = team
                row_data["school_name"] = team_tag.text
            # Extracting other columns
            tds = row.find_all("td")
            for td in tds:
                column_name = td.get("data-stat")
                # skip columns: DUMMY is a set of empty columns, school_name is already extracted
                if column_name not in ["DUMMY", "school_name"]:
                    row_data[column_name] = td.text.strip()
                # print(row_data)
            teams_data.append(row_data)

    df = pd.DataFrame(teams_data, columns=list(teams_data[0].keys()))
    df["year"] = year
    return df


def get_all_teams(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df_year = df[df["year"] == year]
    all_teams_lst = list(df_year["team"].unique())
    return pd.DataFrame(all_teams_lst, columns=["team"])


def main():
    # Parse the command-line arguments
    parser = get_parser()
    args = parser.parse_args()

    table_name = "sports_ref_team_stats"

    if args.dry_run:
        print(f"Running in dry-run mode for {args.year}.")
        df = create_team_stats(args.year)
        print(df)
        return

    # call the function with the command-line arguments
    df = hf.generate_data_all_years(
        create_team_stats,
        year=args.year,
        recompute=args.recompute,
        table_name=table_name,
    )

    # write the dataframe to a csv
    file_path = f"{hf.get_generated_dir(args.year)}/{table_name}.csv"
    hf.write_to_csv(df, file_path, args.overwrite)

    # create a pickled dataframe of all teams for given year
    all_teams = get_all_teams(df, args.year)
    all_teams.to_pickle(f"{hf.get_generated_dir(args.year)}/all_teams.pkl")


if __name__ == "__main__":
    main()
