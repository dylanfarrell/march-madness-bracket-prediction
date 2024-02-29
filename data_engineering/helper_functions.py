import numpy as np
import pandas as pd
from datetime import datetime
from constants import KAGGLE_DIR, KAGGLE_DIR_LAST_YR, CURRENT_YR


def get_kaggle_dir(yr: int) -> str:
    return f"../data/{yr}/kaggle_data"


def get_generated_dir(yr: int) -> str:
    return f"../data/{yr}/generated_data"


# retrieve team name by id
def team_lookup(id: int) -> str:
    """
    Retrieves a team name given its id

    :param id_num: kaggle team id (int)
    :return: team name (str)
    """
    teams = pd.read_csv(f"{KAGGLE_DIR}/MTeams.csv")
    return teams[teams["TeamID"] == id]["TeamName"].values[0]


# add team spellings to the team spellings csv
def update_team_spellings_file(unmatched_spellings_lst: list[tuple[str, int]]) -> None:
    """
    Takes in a list of (team spelling, team id) tuples and adds them to
    the list of valid team spellings

    :param unmatched_spellings_lst: list of (team spelling, team id) tuples
    :return: nothing, just updates the MTeamSpellings csv
    """
    team_spellings = pd.read_csv(
        f"{KAGGLE_DIR}/MTeamSpellings.csv", encoding="unicode_escape"
    )
    unmatched_spellings = pd.DataFrame(
        {
            "TeamNameSpelling": [spelling for spelling, _ in unmatched_spellings_lst],
            "TeamID": [teamid for _, teamid in unmatched_spellings_lst],
        }
    )
    full_spellings = pd.concat([team_spellings, unmatched_spellings], ignore_index=True)
    full_spellings.drop_duplicates(inplace=True)
    full_spellings.to_csv(f"{KAGGLE_DIR}/MTeamSpellings.csv", index=False)


# join outside data source to team spellings csv to get kaggle team id
def scraped_df_join_to_team_spellings(
    scraped_df: pd.DataFrame, team_col: str = "school"
) -> pd.DataFrame:
    """Joins a scraped table without kaggle team ids to the kaggle team spellings file
    to get the associated team id
    Note: if the team spelling doesn't exist in the kaggle team spelling table,
    it will drop that team from the table

    :param scraped_table: the outside data source table you want ids for
    :param team_col: the school/team name (i.e. 'team' or 'school' or 'TeamName') to join on
    :return: a joined table with kaggle ids
    """
    team_spellings = load_kaggle_data("MTeamSpellings")
    joined_df = team_spellings.merge(
        scraped_df, left_on="TeamNameSpelling", right_on=team_col
    )
    # joined_df.drop("TeamNameSpelling", axis=1, inplace=True)
    return joined_df


# outputs the team spellings from the scraped table that don't appear in the kaggle table
def check_for_missing_spellings(
    scraped_df: pd.DataFrame, joined_df: pd.DataFrame, team_col: str = "season"
) -> list:
    """
    Rejoins the joined table to the scraped table. Honestly should handle this all
    in the scraped_df_join function but will handle that next year.
    """
    comp = scraped_df.merge(joined_df, on=team_col, how="left")
    return list(np.unique(comp[comp["TeamID"].isna()][team_col]))


def load_kaggle_data(table_name: str) -> pd.DataFrame:
    """Try loading kaggle data from this year. If it fails, load from last year."""
    try:
        # Try loading the file from this year's data
        df = pd.read_csv(f"{KAGGLE_DIR}/{table_name}.csv")
        return df
    except FileNotFoundError:
        # If the file is not found, try loading from last year's data
        try:
            df = pd.read_csv(f"{KAGGLE_DIR_LAST_YR}/{table_name}.csv")
            print(
                f"File for {table_name} from {CURRENT_YR} not found. Loaded {CURRENT_YR - 1} data instead."
            )
            return df
        # If neither is found, let user know
        except FileNotFoundError:
            print(
                f"File for {table_name} not found in {CURRENT_YR} or {CURRENT_YR - 1}. Please check table name spelling."
            )
