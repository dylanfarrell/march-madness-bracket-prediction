import warnings

import numpy as np
import pandas as pd
from scipy.linalg import eig
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm

from argparser_config import get_parser
import helper_functions as hf


def sorted_id(r):
    return ",".join(sorted([r["WTeamID"], r["LTeamID"]]))


def get_home_away(r):
    if r["WLoc"] == "H":
        return r["WTeamID"], r["LTeamID"]
    elif r["WLoc"] == "A":
        return r["LTeamID"], r["WTeamID"]
    return "NA", "NA"


def get_home_away_score(r):
    if r["WLoc"] == "H":
        return r["WScore"], r["LScore"]
    elif r["WLoc"] == "A":
        return r["LScore"], r["WScore"]
    return np.nan, np.nan


def get_dif(r):
    if r["game_num"] == 1:
        return r["home_score"] - r["away_score"]
    return r["away_score"] - r["home_score"]


def get_team1_loc(r):
    if r["Team1"] == r["home_id"]:
        return "H"
    elif r["Team1"] == r["away_id"]:
        return "A"
    return "N"


def get_team1_diff(r):
    if r["Team1"] == r["WTeamID"]:
        return r["WScore"] - r["LScore"]
    return r["LScore"] - r["WScore"]


def fit_home_court_model(regular_seasons: pd.DataFrame) -> tuple[LogisticRegression, int]:
    home_and_home = regular_seasons.groupby(["home_id", "away_id"]).head(1).copy()
    home_and_home["matchups"] = home_and_home.groupby(["Season", "sorted_ids"])["Season"].transform("size")
    home_and_home = home_and_home[home_and_home.matchups == 2]
    home_and_home["game_num"] = home_and_home.groupby(["Season", "sorted_ids"])["DayNum"].cumcount() + 1
    home_and_home["home_score"] = home_and_home.apply(
        lambda r: r["WScore"] if r["WLoc"] == "H" else r["LScore"], axis=1
    )
    home_and_home["away_score"] = home_and_home.apply(
        lambda r: r["WScore"] if r["WLoc"] == "A" else r["LScore"], axis=1
    )
    home_and_home["dif"] = home_and_home.apply(get_dif, axis=1)
    home_and_home.set_index(["sorted_ids", "game_num"], inplace=True)
    home_and_home = home_and_home[["dif"]].unstack()
    home_and_home.columns = home_and_home.columns.get_level_values(1)
    home_and_home["away_win"] = (home_and_home[2] > 0).map(int)

    train_x = np.expand_dims(home_and_home[1].values, axis=-1)
    train_y = home_and_home["away_win"].values
    lr_model = LogisticRegression()
    lr_model.fit(train_x, train_y)

    x_values = np.array(range(-100, 101))
    odds = np.exp(x_values * lr_model.coef_ + lr_model.intercept_)
    prob = odds / (1.0 + odds)
    s_x_h = pd.DataFrame(data=prob[0], index=x_values, columns=["prob"])
    home_court_advantage = int((s_x_h["prob"] - 0.500).abs().idxmin())

    print(f"Logistic regression coef: {lr_model.coef_[0][0]:.6f}, intercept: {lr_model.intercept_[0]:.6f}")
    print(f"Home court advantage: {home_court_advantage} pts")

    return lr_model, home_court_advantage


def build_transition_prob_lookup(
    lr_model: LogisticRegression, home_court_advantage: int
) -> pd.DataFrame:
    x_values = np.array(range(-100, 101))

    odds_h = np.exp((x_values + home_court_advantage) * lr_model.coef_ + lr_model.intercept_)
    r_x_h = pd.DataFrame(data=(odds_h / (1.0 + odds_h))[0], index=x_values, columns=["H"])

    helper_df = 1.0 - r_x_h
    helper_df.index = range(100, -101, -1)
    r_x_a = helper_df.sort_index()
    r_x_a.columns = ["A"]

    odds_n = np.exp((x_values + 2 * home_court_advantage) * lr_model.coef_ + lr_model.intercept_)
    r_x_n = pd.DataFrame(data=(odds_n / (1.0 + odds_n))[0], index=x_values, columns=["N"])

    game2_probs = pd.concat([r_x_h, r_x_a, r_x_n], axis=1)
    game2_probs.reset_index(inplace=True)
    game2_probs.columns = ["diff", "H", "A", "N"]
    return pd.melt(game2_probs, id_vars="diff", var_name="loc", value_name="prob")


def prepare_regular_seasons(
    regular_seasons: pd.DataFrame, t_prob_lookup: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    regular_seasons["Team1"] = regular_seasons["sorted_ids"].apply(lambda x: x.split(",")[0])
    regular_seasons["Team2"] = regular_seasons["sorted_ids"].apply(lambda x: x.split(",")[1])
    regular_seasons["Team1_loc"] = regular_seasons.apply(get_team1_loc, axis=1)
    regular_seasons["Team1_diff"] = regular_seasons.apply(get_team1_diff, axis=1)
    regular_seasons["prob_t1_better"] = pd.merge(
        regular_seasons, t_prob_lookup, how="left",
        left_on=["Team1_loc", "Team1_diff"], right_on=["loc", "diff"],
    )["prob"]
    regular_seasons["prob_t2_better"] = 1 - regular_seasons["prob_t1_better"]

    wins = regular_seasons.groupby(["Season", "WTeamID"], as_index=False).size()
    wins.columns = ["Season", "TeamID", "Wins"]
    losses = regular_seasons.groupby(["Season", "LTeamID"], as_index=False).size()
    losses.columns = ["Season", "TeamID", "Losses"]
    games = pd.merge(wins, losses, how="outer", on=["Season", "TeamID"]).fillna(0)
    games["Total"] = games["Wins"] + games["Losses"]

    t_prob_team_lookup = regular_seasons.groupby(
        ["Season", "Team1", "Team2"], as_index=False
    )[["prob_t1_better", "prob_t2_better"]].sum()
    t_prob_team_lookup["Team1_Games"] = pd.merge(
        t_prob_team_lookup, games, how="left", left_on=["Season", "Team1"], right_on=["Season", "TeamID"]
    )["Total"]
    t_prob_team_lookup["Team2_Games"] = pd.merge(
        t_prob_team_lookup, games, how="left", left_on=["Season", "Team2"], right_on=["Season", "TeamID"]
    )["Total"]
    t_prob_team_lookup["prob_t1_normalized"] = t_prob_team_lookup["prob_t1_better"] / t_prob_team_lookup["Team2_Games"]
    t_prob_team_lookup["prob_t2_normalized"] = t_prob_team_lookup["prob_t2_better"] / t_prob_team_lookup["Team1_Games"]

    return regular_seasons, t_prob_team_lookup


def get_transition(yr, regular_seasons, t_prob_team_lookup):
    cols = ["Season", "Team1", "Team2", "prob_t1_normalized", "prob_t2_normalized"]
    temp = t_prob_team_lookup[t_prob_team_lookup.Season == yr][cols].copy()
    t1s = list(regular_seasons[regular_seasons.Season == yr]["Team1"].unique())
    t2s = list(regular_seasons[regular_seasons.Season == yr]["Team2"].unique())
    tms = list(set(t1s + t2s))
    new_df = pd.DataFrame([(yr, x, x, 0, 0) for x in tms], columns=cols)
    new_df2 = pd.concat([temp, new_df], ignore_index=True)
    t1_matrix = new_df2.pivot(index="Team1", columns="Team2", values="prob_t2_normalized").fillna(0.0)
    t2_matrix = new_df2.pivot(index="Team2", columns="Team1", values="prob_t1_normalized").fillna(0.0)
    t_matrix = t1_matrix.add(t2_matrix)
    for t in t_matrix.index:
        t_matrix.loc[t, t] = 1.0 - t_matrix.loc[t, :].sum()
    return t_matrix


def get_stationary(t_matrix):
    eigenvalues, eigenvectors = eig(t_matrix, left=True, right=False)
    stationary = eigenvectors[:, 0]
    stationary = stationary / np.sum(stationary)
    if stationary[np.iscomplex(stationary)].shape[0] == 0:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stationary = stationary.astype(float)
    else:
        print("Warning: complex eigenvalues detected!")
    return pd.DataFrame(data=list(zip(t_matrix.index, stationary)), columns=["TeamID", "pi_i"])


def create_stationary_probabilities(year: int, mode: str) -> pd.DataFrame:
    kaggle_dir = hf.get_kaggle_dir(year, mode)
    regular_seasons = pd.read_csv(
        f"{kaggle_dir}/{mode}RegularSeasonCompactResults.csv",
        dtype={"WTeamID": str, "LTeamID": str},
    )

    regular_seasons["sorted_ids"] = regular_seasons.apply(sorted_id, axis=1)
    regular_seasons["matchups"] = regular_seasons.groupby(["Season", "sorted_ids"])["Season"].transform("size")
    regular_seasons["home_id"], regular_seasons["away_id"] = zip(
        *regular_seasons.apply(get_home_away, axis=1)
    )
    regular_seasons["home_score"], regular_seasons["away_score"] = zip(
        *regular_seasons.apply(get_home_away_score, axis=1)
    )

    lr_model, home_court_advantage = fit_home_court_model(regular_seasons)
    t_prob_lookup = build_transition_prob_lookup(lr_model, home_court_advantage)
    regular_seasons, t_prob_team_lookup = prepare_regular_seasons(regular_seasons, t_prob_lookup)

    stationary_dfs = []
    for season in tqdm(regular_seasons.Season.unique(), desc="Computing stationary distributions"):
        t_matrix = get_transition(season, regular_seasons, t_prob_team_lookup)
        stationary_df = get_stationary(t_matrix)
        stationary_df["year"] = season
        stationary_dfs.append(stationary_df)

    markov_df = pd.concat(stationary_dfs, ignore_index=True)
    return markov_df[["year", "TeamID", "pi_i"]]


def main():
    parser = get_parser()
    args = parser.parse_args()
    df = create_stationary_probabilities(args.year, args.mode)

    file_path = f"{hf.get_generated_dir(args.year, args.mode)}/stationary_probabilities.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
