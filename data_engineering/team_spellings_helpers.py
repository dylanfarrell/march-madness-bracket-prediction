import helper_functions as hf
from argparser_config import get_parser
from constants import CURRENT_YR


def update_team_spellings(year: int = CURRENT_YR):
    team_spellings_prev = hf.load_team_spellings(year - 1)
    team_spellings_cur = hf.load_team_spellings(year)

    merged_df = team_spellings_cur.merge(
        team_spellings_prev,
        how="outer",
        on="TeamNameSpelling",
        indicator=True,
        suffixes=("_this_year", "_last_year"),
    )
    # drop corrupted rows -- they've all contained the characters below
    merged_df = merged_df[~merged_df["TeamNameSpelling"].str.contains("Ãƒ")]

    # new teams are ones that are only on the left side of the join
    new_teams = merged_df[merged_df["_merge"] == "left_only"][
        "TeamNameSpelling"
    ].tolist()
    print(f"The following teams are new this year: {new_teams}")

    # old teams are ones that are only on the right side of the join
    old_teams = merged_df[merged_df["_merge"] == "right_only"][
        "TeamNameSpelling"
    ].tolist()
    print(f"The following teams have been manually added in years past: {old_teams}")

    # coalesce the teams ids into one column
    merged_df["TeamID"] = merged_df["TeamID_this_year"].combine_first(
        merged_df["TeamID_last_year"]
    )

    # drop the columns created by the merge
    merged_df.drop(
        columns=["TeamID_this_year", "TeamID_last_year", "_merge"], inplace=True
    )

    return merged_df


def main():
    # parse the command-line arguments
    parser = get_parser()
    args = parser.parse_args()

    table_name = "MTeamSpellings"

    df = update_team_spellings(args.year)

    # write the dataframe to a csv
    file_path = f"{hf.get_kaggle_dir(args.year)}/{table_name}.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
