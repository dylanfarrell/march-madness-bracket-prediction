import time
import numpy as np
import pandas as pd
from datetime import datetime
import os
import urllib.request
from bs4 import BeautifulSoup
from typing import Callable
from constants import DATA_START_YR, KAGGLE_DIR, KAGGLE_DIR_LAST_YR, CURRENT_YR

## DATA LOADING


def get_kaggle_dir(yr: int) -> str:
    return f"../data/{yr}/kaggle_data"


def get_generated_dir(yr: int) -> str:
    return f"../data/{yr}/generated_data"


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


def load_and_trim(
    table_name: str, start_yr: int, season_col: str = "Season"
) -> pd.DataFrame:
    df = load_kaggle_data(table_name)
    print(f"Trimming data to {start_yr}.")
    return df[df[season_col] >= start_yr].reset_index(drop=True)


def get_soup(link: str, rate_limit: bool = True) -> BeautifulSoup:
    with urllib.request.urlopen(link) as url:
        page = url.read()
    # handle rate limiting inside the request function
    # 20 calls/min is max, so sleep for 3 seconds (plus script will add time to run anyway)
    # set to True out of precaution, can set to False for one-offs
    if rate_limit:
        time.sleep(3)
    return BeautifulSoup(page, "html.parser")


# function to return all sports reference team names in list form
def get_all_sports_ref_teams(year: int = CURRENT_YR) -> list[str]:
    all_teams = pd.read_pickle(f"{get_generated_dir(year)}/all_schools.pkl")
    return all_teams["school_id"].tolist()


## DATA WRITING


# handles writing data with the overwrite flag
def write_to_csv(df: pd.DataFrame, file_path: str, overwrite: bool) -> None:
    if not os.path.exists(file_path) or overwrite:
        df.to_csv(file_path, index=False)
        print(f"Data written to {file_path}.")
    else:
        print(
            "This file already exists. The overwrite flag is set to False so the existing file was not overwritten."
        )


# WIP
def generate_data_all_years(
    function: Callable,
    year: int,
    start_year: int = DATA_START_YR,
    backfill: bool = False,
) -> None:
    if backfill:
        preseason_rankings = function(DATA_START_YR)
        preseason_joined = scraped_df_join_to_team_spellings(preseason_rankings)
        for yr in range(DATA_START_YR + 1, year + 1):
            # print(yr)
            new_preseason_rankings = function(yr)
            new_preseason_joined = scraped_df_join_to_team_spellings(
                new_preseason_rankings
            )
            preseason_joined = pd.concat(
                [preseason_joined, new_preseason_joined], ignore_index=True
            )
            # print(check_for_missing_spellings(new_preseason_rankings, new_preseason_joined))
    else:
        preseason_rankings = function(year)
        preseason_joined = scraped_df_join_to_team_spellings(preseason_rankings)
        preseason_rankings_historic = pd.read_csv(
            f"{get_generated_dir(year - 1)}/{filler}.csv"
        )
        preseason_joined = pd.concat(
            [preseason_joined, preseason_rankings_historic], ignore_index=True
        )
    preseason_joined.drop("TeamNameSpelling", axis=1, inplace=True)


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
