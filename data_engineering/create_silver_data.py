import pandas as pd

import helper_functions as hf
from argparser_config import get_parser


def add_kaggle_id(df, team_col: str = "team") -> pd.DataFrame:
    team_spellings = hf.load_kaggle_data("MTeamSpellings")
    merged_df = df.merge(
        team_spellings, how="inner", left_on=team_col, right_on="TeamNameSpelling"
    )
    merged_df.drop("TeamNameSpelling", axis=1, inplace=True)

    # return list of dropped teams
    dropped_df = df.merge(
        team_spellings,
        how="left",
        left_on=team_col,
        right_on="TeamNameSpelling",
        indicator=True,
    )
    # Filter rows where the '_merge' column is 'left_only', indicating no match in df2
    df1_no_match = dropped_df[dropped_df["_merge"] == "left_only"]
    dropped_teams = df1_no_match[team_col].tolist()
    print(f"The following teams had no id match and were dropped: {dropped_teams}")

    return merged_df


def main():
    parser = get_parser()
    args = parser.parse_args()

    datasets = [
        "coaches_data",
        "preseason_rankings",
        "returning_player_team_stats_tourney",
        "sports_ref_team_stats",
        "team_weighted_info_tourney",
        "stationary_probabilities",
    ]

    for dataset in datasets:
        df = hf.load_generated_data(dataset)
        if dataset != "stationary_probabilities":
            print(f"Adding kaggle ids to: {dataset}")
            df_silver = add_kaggle_id(df)
        else:
            df_silver = df
        file_path = f"{hf.get_silver_dir(args.year)}/{dataset}_silver.csv"
        hf.write_to_csv(df_silver, file_path, args.overwrite)


if __name__ == "__main__":
    main()
