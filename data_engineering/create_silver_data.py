import helper_functions as hf


def add_kaggle_id(df, team_col: str = "team"):
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
    datasets = [
        "coaches_data",
        # "preseason_rankings",
        "returning_player_team_stats",
        "sports_reference_team_stats",
        "team_weighted_info",
    ]

    for dataset in datasets:
        print(dataset)
        df = hf.load_generated_data(dataset)
        hf.add_kaggle_id(df)


if __name__ == "__main__":
    main()
