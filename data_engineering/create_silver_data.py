import pandas as pd

import helper_functions as hf
from argparser_config import get_parser
from constants import MENS_GENERATED_DATASETS, WOMENS_GENERATED_DATASETS


def add_kaggle_id(
    df: pd.DataFrame, year: int, mode: str, team_col: str = "team"
) -> pd.DataFrame:
    team_spellings = hf.load_team_spellings(year, mode)
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

    datasets_already_silver = ["stationary_probabilities"]
    datasets = (
        WOMENS_GENERATED_DATASETS if args.mode == "W" else MENS_GENERATED_DATASETS
    )

    for dataset in datasets:
        try:
            df = hf.load_generated_data(dataset, args.year, args.mode)
            if dataset not in datasets_already_silver:
                print(f"Adding kaggle ids to: {dataset}")
                df_silver = add_kaggle_id(df, args.year, args.mode)
            else:
                print(f"Dataset {dataset} already has kaggle ids.")
                df_silver = df
            file_path = (
                f"{hf.get_silver_dir(args.year, args.mode)}/{dataset}_silver.csv"
            )
            hf.write_to_csv(df_silver, file_path, args.overwrite)
        except FileNotFoundError:
            print(f"File for {dataset} not found in {args.year}/{args.mode}.")


if __name__ == "__main__":
    main()
