import os
import time
from typing import Callable

import numpy as np
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import DATA_START_YR, CURRENT_YR

## DATA LOADING


# returns kaggle data directory stub for a given year
def get_kaggle_dir(year: int) -> str:
    return f"../data/{year}/kaggle_data"


# returns generated data directory stub for a given year
def get_generated_dir(year: int) -> str:
    return f"../data/{year}/generated_data"


# returns silver data directory stub for a given year
def get_silver_dir(year: int) -> str:
    return f"../data/{year}/silver_data"


# returns gold data directory stub for a given year
def get_gold_dir(year: int) -> str:
    return f"../data/{year}/gold_data"


# load a kaggle dataset, fall back on previous year
def load_kaggle_data(
    table_name: str, year: int = CURRENT_YR, encoding: str | None = None
) -> pd.DataFrame:
    """Try loading kaggle data from this year. If it fails, load from last year."""
    try:
        # Try loading the file from the specified year's data
        df = pd.read_csv(f"{get_kaggle_dir(year)}/{table_name}.csv", encoding=encoding)
        return df
    except FileNotFoundError:
        print(
            f"File for {table_name} not found in {year}. Please check table name spelling."
        )


# load a kaggle dataset and trim it to a given year
def load_and_trim(
    table_name: str, start_yr: int = DATA_START_YR, season_col: str = "Season"
) -> pd.DataFrame:
    df = load_kaggle_data(table_name)
    print(f"Trimming data to {start_yr}.")
    return df[df[season_col] >= start_yr].reset_index(drop=True)


# load the MTeamSpellings table -- often the backbone for script iteration
def load_team_spellings(year: int = CURRENT_YR) -> pd.DataFrame:
    table_name = "MTeamSpellings"
    encoding = "Windows-1252"
    try:
        return load_kaggle_data(table_name, year, encoding)
    except FileNotFoundError:
        try:
            df = load_kaggle_data(table_name, year - 1, encoding)
            print(
                f"File for {table_name} from {year} not found. Loaded {year - 1} data instead."
            )
            return df
        except FileNotFoundError:
            print(
                f"File for {table_name} not found in {year} or {year - 1}. Please check table name spelling."
            )


# load a generated dataset, fall back on previous year
def load_generated_data(table_name: str, year: int = CURRENT_YR) -> pd.DataFrame:
    """Try loading generated data from this year. If it fails, load from last year."""
    try:
        # Try loading the file from this year's data
        return pd.read_csv(f"{get_generated_dir(year)}/{table_name}.csv")
    except FileNotFoundError:
        print(
            f"File for {table_name} not found in {year}. Please check table name spelling."
        )


# load silver data
def load_silver_data(table_name: str, year: int = CURRENT_YR) -> pd.DataFrame:
    """Try loading silver data from this year."""
    file_path = f"{get_silver_dir(year)}/{table_name}.csv"
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found.")


# get a BeautifulSoup object from a url
def get_soup(link: str, rate_limit: bool = True) -> BeautifulSoup:
    with urllib.request.urlopen(link) as url:
        page = url.read()
    # handle rate limiting inside the request function
    # 20 calls/min is max, so sleep for 3 seconds (plus script will add time to run anyway)
    # set to True out of precaution, can set to False for one-offs
    if rate_limit:
        time.sleep(3)
    return BeautifulSoup(page, "html.parser")


def try_cast(value: str, cast_type, fallback_value):
    try:
        return cast_type(value)  # This will also raise ValueError
    except ValueError:
        return fallback_value


# function to return all sports reference team names in list form
def get_sports_ref_teams(
    year: int = CURRENT_YR, tourney_teams_only: bool = False
) -> list[str]:
    if year < 2022:
        dir_year = 2022
    else:
        dir_year = year

    all_teams = pd.read_pickle(f"{get_generated_dir(dir_year)}/all_teams.pkl")
    if not tourney_teams_only:
        return list(all_teams["team"])
    else:
        team_spellings = load_team_spellings(year)
        # filter team_spellings down to only the sports ref spellings
        # team_spellings also has kaggle_ids
        df_joined = team_spellings.merge(
            all_teams, how="inner", left_on="TeamNameSpelling", right_on="team"
        )
        tourney_seeds = load_kaggle_data("MNCAATourneySeeds")
        tourney_seeds = tourney_seeds[tourney_seeds["Season"] == year]
        tourney_teams = df_joined.merge(tourney_seeds, how="inner", on="TeamID")
        return list(tourney_teams["team"])


## DATA WRITING


# handles writing data with the overwrite flag
def write_to_csv(df: pd.DataFrame, file_path: str, overwrite: bool) -> None:
    if not os.path.exists(file_path) or overwrite:
        df.to_csv(file_path, index=False)
        print(f"Success: data written to {file_path}.")
    else:
        print(
            f"{file_path} already exists. The overwrite flag is set to False so the existing file was not overwritten."
        )


# function to write data by either recomputing the data for all years
# or by appending the new year's data to the existing data
def generate_data_all_years(
    function: Callable,
    year: int,
    start_year: int = DATA_START_YR,
    recompute: bool = False,
    table_name: str | None = None,
    **kwargs,
) -> pd.DataFrame:
    if not recompute and table_name is None:
        raise ValueError("If recompute is False, you must provide a table name.")
    elif recompute:
        print(f"Recomputing data starting from {start_year}.")
        base_df = function(start_year, **kwargs)
        for year in tqdm(range(start_year + 1, year + 1), desc="Processing years"):
            next_year_df = function(year, **kwargs)
            base_df = pd.concat([base_df, next_year_df], ignore_index=True)
    else:
        new_year_df = function(year, **kwargs)
        base_df = pd.read_csv(f"{get_generated_dir(year - 1)}/{table_name}.csv")
        base_df = pd.concat([base_df, new_year_df], ignore_index=True)
    return base_df


# retrieve team name by id
def team_lookup(id: int, year: int = CURRENT_YR) -> str:
    """
    Retrieves a team name given its id

    :param id_num: kaggle team id (int)
    :return: team name (str)
    """
    teams = pd.read_csv(f"{get_kaggle_dir(year)}/MTeams.csv")
    return teams[teams["TeamID"] == id]["TeamName"].values[0]


# add team spellings to the team spellings csv
def update_team_spellings_file(unmatched_spellings_lst: list[tuple[str, int]]) -> None:
    """
    Takes in a list of (team spelling, team id) tuples and adds them to
    the list of valid team spellings

    :param unmatched_spellings_lst: list of (team spelling, team id) tuples
    :return: nothing, just updates the MTeamSpellings csv
    """
    team_spellings = load_team_spellings()
    unmatched_spellings = pd.DataFrame(
        {
            "TeamNameSpelling": [spelling for spelling, _ in unmatched_spellings_lst],
            "TeamID": [teamid for _, teamid in unmatched_spellings_lst],
        }
    )
    full_spellings = pd.concat([team_spellings, unmatched_spellings], ignore_index=True)
    full_spellings.drop_duplicates(inplace=True)
    full_spellings.to_csv(f"{get_kaggle_dir()}/MTeamSpellings.csv", index=False)


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
