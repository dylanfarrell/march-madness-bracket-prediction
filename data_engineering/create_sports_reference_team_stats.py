import pandas as pd

import helper_functions as hf
from argparser_config import get_parsed_args
from constants import SPORTS_REF_STUB


def create_team_stats(year: int) -> pd.DataFrame:
    link = f"{SPORTS_REF_STUB}/cbb/seasons/men/{year}-school-stats.html"
    soup = hf.get_soup(link)

    teams_data = []

    # Identify the header row to get column names (excluding the first "Rk" and last "School" headers as they're processed separately)
    header_row = soup.find("thead").find_all("tr")[
        1
    ]  # Assuming the second row in thead is the relevant one
    column_names = [header.text for header in header_row.find_all("th")][
        1:
    ]  # Skip 'Rk', include 'School' and onwards

    # Find the table body
    table_body = soup.find("tbody")
    if table_body:
        # Find all rows in the table body
        rows = table_body.find_all("tr")
        for row in rows:
            row_data = {}
            # Extracting School Name and ID
            school_tag = row.find("a")
            if school_tag:
                school_name = school_tag.text
                school_id = school_tag["href"].split("/")[3]  # Extract school ID
                row_data["School Name"] = school_name
                row_data["team"] = school_id
            # Extracting other columns
            data_points = row.find_all("td")
            for column_name, data_point in zip(column_names, data_points):
                # print(column_name)
                row_data[column_name] = data_point.text.strip()
            teams_data.append(row_data)

    df = pd.DataFrame(teams_data, columns=["team"] + column_names)
    df["year"] = year
    df = df.dropna(subset=["School"]).reset_index(drop=True)

    return df


def get_all_teams(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df_year = df[df["year"] == year]
    all_teams_lst = list(df_year["team"].unique())
    return pd.DataFrame(all_teams_lst, columns=["team"])


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

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
