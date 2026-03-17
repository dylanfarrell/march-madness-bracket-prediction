import glob
import numpy as np
import pandas as pd
from pandasql import sqldf
from ast import literal_eval
from argparser_config import get_parser
import helper_functions as hf
from constants import DATA_START_YR


def compute_possessions_and_efficiency(detailed: pd.DataFrame) -> pd.DataFrame:
    detailed = detailed.copy()
    detailed['WPos'] = 0.96 * (
        detailed['WFGA'] + detailed['WTO'] + 0.44 * detailed['WFTA'] - detailed['WOR']
    )
    detailed['LPos'] = 0.96 * (
        detailed['LFGA'] + detailed['LTO'] + 0.44 * detailed['LFTA'] - detailed['LOR']
    )
    detailed['Pace'] = (
        (200 / (200 + 5 * 5 * detailed['NumOT']))
        * (detailed['WPos'] + detailed['LPos']) / 2
    )
    detailed['WOffEff'] = 100 * (detailed['WScore'] / detailed['WPos'])
    detailed['LOffEff'] = 100 * (detailed['LScore'] / detailed['LPos'])
    return detailed


def aggregate_season_stats(regular_season_detailed: pd.DataFrame) -> pd.DataFrame:
    wins = sqldf('''
        SELECT
            Season, WTeamID AS TeamID,
            COUNT() as num_wins,
            GROUP_CONCAT(WScore - LScore) as winning_margins,
            SUM(WScore) sum_score,
            SUM(LScore) sum_score_of_opponents,
            SUM(CASE WHEN WLoc == 'A' OR WLoc == 'N' THEN 1 ELSE 0 END) non_home_wins,
            SUM(CASE WHEN WScore - LScore <= 3 OR NumOT > 0 THEN 1 ELSE 0 END) close_wins,
            SUM(WFGA3) sum_3FGA,
            SUM(WFGM3) sum_3FGM,
            SUM(WFTA) sum_FTA,
            SUM(WFTM) sum_FTM,
            SUM(WTO) sum_TOV,
            SUM(Pace) sum_pace,
            SUM(WOffEff) sum_off_eff,
            SUM(LOffEff) sum_def_eff
        FROM regular_season_detailed
        GROUP BY 1, 2
    ''')

    losses = sqldf('''
        SELECT
            Season, LTeamID AS TeamID,
            COUNT() as num_losses,
            GROUP_CONCAT(LScore - WScore) as losing_margins,
            SUM(LScore) sum_score,
            SUM(WScore) sum_score_of_opponents,
            SUM(CASE WHEN WLoc == 'A' THEN 1 ELSE 0 END) home_losses,
            SUM(CASE WHEN WScore - LScore <= 3 OR NumOT > 0 THEN 1 ELSE 0 END) close_losses,
            SUM(LFGA3) sum_3FGA,
            SUM(LFGM3) sum_3FGM,
            SUM(LFTA) sum_FTA,
            SUM(LFTM) sum_FTM,
            SUM(LTO) sum_TOV,
            SUM(Pace) sum_pace,
            SUM(LOffEff) sum_off_eff,
            SUM(WOffEff) sum_def_eff
        FROM regular_season_detailed
        GROUP BY 1, 2
    ''')

    stats = wins.merge(losses, on=['Season', 'TeamID'], how='outer', suffixes=('_w', '_l'))
    stats.fillna(0, inplace=True)
    stats[['num_wins', 'num_losses']] = stats[['num_wins', 'num_losses']].astype(int)
    stats[['winning_margins', 'losing_margins']] = stats[['winning_margins', 'losing_margins']].astype(str)

    stats['total_games'] = stats['num_wins'] + stats['num_losses']
    stats['total_points_for'] = stats['sum_score_w'] + stats['sum_score_l']
    stats['total_points_against'] = stats['sum_score_of_opponents_w'] + stats['sum_score_of_opponents_l']
    stats['win_pct'] = stats['num_wins'] / stats['total_games']
    stats['avg_points_for'] = stats['total_points_for'] / stats['total_games']
    stats['avg_points_against'] = stats['total_points_against'] / stats['total_games']
    stats['3FGA_pg'] = (stats['sum_3FGA_w'] + stats['sum_3FGA_l']) / stats['total_games']
    stats['3FGM_pg'] = (stats['sum_3FGM_w'] + stats['sum_3FGM_l']) / stats['total_games']
    stats['3_pct'] = stats['3FGM_pg'] / stats['3FGA_pg']
    stats['FTA_pg'] = (stats['sum_FTA_w'] + stats['sum_FTA_l']) / stats['total_games']
    stats['FTM_pg'] = (stats['sum_FTM_w'] + stats['sum_FTM_l']) / stats['total_games']
    stats['FT_pct'] = stats['FTM_pg'] / stats['FTA_pg']
    stats['TOV_pg'] = (stats['sum_TOV_w'] + stats['sum_TOV_l']) / stats['total_games']

    stats['differential_arr'] = [
        literal_eval(wm + ',' + lm)
        for wm, lm in zip(stats['winning_margins'], stats['losing_margins'])
    ]
    stats['avg_game_margin'] = [np.mean(arr) for arr in stats['differential_arr']]
    stats['std_game_margin'] = [np.std(arr) for arr in stats['differential_arr']]

    stats['avg_pace'] = (stats['sum_pace_w'] + stats['sum_pace_l']) / stats['total_games']
    stats['off_eff'] = (stats['sum_off_eff_w'] + stats['sum_off_eff_l']) / stats['total_games']
    stats['def_eff'] = (stats['sum_def_eff_w'] + stats['sum_def_eff_l']) / stats['total_games']

    k = 13.91
    stats['pythag_win_pct'] = (stats['total_points_for'] ** k) / (
        stats['total_points_for'] ** k + stats['total_points_against'] ** k
    )
    stats['luck'] = stats['win_pct'] - stats['pythag_win_pct']

    compact_cols = [
        'Season', 'TeamID', 'total_games', 'num_wins', 'num_losses', 'win_pct',
        'avg_points_for', 'avg_points_against', 'avg_game_margin', 'std_game_margin',
        'non_home_wins', 'home_losses', 'close_wins', 'close_losses',
        '3FGA_pg', '3FGM_pg', '3_pct', 'FTM_pg', 'FTA_pg', 'FT_pct', 'TOV_pg',
        'avg_pace', 'off_eff', 'def_eff', 'pythag_win_pct', 'luck',
    ]
    return stats[compact_cols]


def compute_tourney_team_stats(
    regular_season_compact: pd.DataFrame, seeds: pd.DataFrame
) -> pd.DataFrame:
    team_seeds = sqldf('''
        SELECT
            a.*, b.Seed WTeamSeed, c.Seed LTeamSeed
        FROM regular_season_compact a
        LEFT JOIN seeds b
            ON a.WTeamID = b.TeamID AND a.Season = b.Season
        LEFT JOIN seeds c
            ON a.LTeamID = c.TeamID AND a.Season = c.Season
    ''')
    team_seeds[['WTeamSeed', 'LTeamSeed']] = team_seeds[['WTeamSeed', 'LTeamSeed']].astype(str)

    wins_tourney = sqldf('''
        SELECT
            Season, WTeamID AS TeamID, WTeamSeed AS Seed,
            SUM(CASE WHEN LTeamSeed != 'None' THEN 1 ELSE 0 END) wins_vs_tourney_teams,
            SUM(CASE WHEN LTeamSeed != 'None' AND WLoc != 'H' THEN 1 ELSE 0 END) away_wins_vs_tourney_teams
        FROM team_seeds
        GROUP BY 1, 2
    ''')

    losses_tourney = sqldf('''
        SELECT
            Season, LTeamID AS TeamID, LTeamSeed AS Seed,
            SUM(CASE WHEN WTeamSeed != 'None' THEN 1 ELSE 0 END) losses_vs_tourney_teams,
            SUM(CASE WHEN WTeamSeed = 'None' THEN 1 ELSE 0 END) losses_vs_non_tourney_teams
        FROM team_seeds
        GROUP BY 1, 2
    ''')

    team_season_stats_tourney = wins_tourney.merge(
        losses_tourney, on=['Season', 'TeamID'], how='outer', suffixes=('_w', '_l')
    )

    result = sqldf('''
        SELECT
            Season, TeamID,
            COALESCE(Seed_w, Seed_l) Seed,
            COALESCE(wins_vs_tourney_teams, 0) wins_vs_tourney_teams,
            COALESCE(away_wins_vs_tourney_teams, 0) away_wins_vs_tourney_teams,
            COALESCE(losses_vs_tourney_teams, 0) losses_vs_tourney_teams,
            COALESCE(losses_vs_non_tourney_teams, 0) losses_vs_non_tourney_teams
        FROM team_season_stats_tourney
        GROUP BY 1, 2
    ''')
    result['games_vs_tourney_teams'] = result['wins_vs_tourney_teams'] + result['losses_vs_tourney_teams']
    return result


def compute_rankings(ordinals: pd.DataFrame) -> pd.DataFrame:
    rpi_net_rankings = ordinals[
        (ordinals['SystemName'] == 'NET') | (ordinals['SystemName'] == 'RPI')
    ]

    net_sub_q = '''
        SELECT
            *,
            ROW_NUMBER() OVER(PARTITION BY Season, TeamID ORDER BY RankingDayNum DESC) AS RankingNum
        FROM rpi_net_rankings
    '''
    net_sub = sqldf(net_sub_q)

    net_df = sqldf('''
        WITH net_window AS (
            SELECT
                *,
                ROW_NUMBER() OVER(PARTITION BY Season, TeamID ORDER BY RankingDayNum DESC) AS RankingNum
            FROM rpi_net_rankings
        )
        SELECT
            fp.Season, fp.TeamID,
            fp.final_net, lp.prev_net,
            lp.prev_net - fp.final_net AS net_improvement
        FROM
            (SELECT Season, TeamID, OrdinalRank AS final_net
             FROM net_window
             WHERE RankingNum = 1) fp
        LEFT JOIN
            (SELECT a.Season, a.TeamID, OrdinalRank AS prev_net
             FROM net_window a
             INNER JOIN
                (SELECT Season, MIN(5, MAX(RankingNum)) rank_num
                 FROM net_window
                 GROUP BY Season) b
             ON a.Season = b.Season AND a.RankingNum = b.rank_num) lp
        ON fp.Season = lp.Season AND fp.TeamID = lp.TeamID
    ''')

    pom_rankings = ordinals[ordinals['SystemName'] == 'POM']

    pom_df = sqldf('''
        WITH pom_window AS (
            SELECT
                *,
                ROW_NUMBER() OVER(PARTITION BY Season, TeamID ORDER BY RankingDayNum DESC) AS RankingNum
            FROM pom_rankings
        )
        SELECT
            fp.Season, fp.TeamID,
            fp.final_pom, lp.prev_pom,
            lp.prev_pom - fp.final_pom AS pom_improvement
        FROM
            (SELECT Season, TeamID, OrdinalRank AS final_pom
             FROM pom_window
             WHERE RankingNum = 1) fp
        LEFT JOIN
            (SELECT a.Season, a.TeamID, OrdinalRank AS prev_pom
             FROM pom_window a
             INNER JOIN
                (SELECT Season, MIN(5, MAX(RankingNum)) rank_num
                 FROM pom_window
                 GROUP BY Season) b
             ON a.Season = b.Season AND a.RankingNum = b.rank_num) lp
        ON fp.Season = lp.Season AND fp.TeamID = lp.TeamID
    ''')

    rankings_df = net_df.merge(pom_df, on=['Season', 'TeamID'], how='outer')
    return rankings_df


def create_team_season_features(year: int, mode: str) -> pd.DataFrame:
    kaggle_dir = hf.get_kaggle_dir(year, mode)
    prefix = mode

    regular_season_detailed = pd.read_csv(f'{kaggle_dir}/{prefix}RegularSeasonDetailedResults.csv')
    regular_season_detailed = regular_season_detailed[regular_season_detailed['Season'] >= DATA_START_YR].reset_index(drop=True)

    regular_season_compact = pd.read_csv(f'{kaggle_dir}/{prefix}RegularSeasonCompactResults.csv')
    regular_season_compact = regular_season_compact[regular_season_compact['Season'] >= DATA_START_YR].reset_index(drop=True)

    seeds = pd.read_csv(f'{kaggle_dir}/{prefix}NCAATourneySeeds.csv')
    seeds = seeds[seeds['Season'] >= DATA_START_YR].reset_index(drop=True)

    regular_season_detailed = compute_possessions_and_efficiency(regular_season_detailed)
    season_stats = aggregate_season_stats(regular_season_detailed)
    tourney_stats = compute_tourney_team_stats(regular_season_compact, seeds)

    team_season_preds = season_stats.merge(tourney_stats, on=['Season', 'TeamID'], how='left')

    ordinals_pattern = f'{kaggle_dir}/{prefix}MasseyOrdinals*.csv'
    ordinals_files = glob.glob(ordinals_pattern)
    if ordinals_files:
        ordinals = pd.read_csv(ordinals_files[0])
        rankings_df = compute_rankings(ordinals)
        team_season_preds = team_season_preds.merge(rankings_df, on=['Season', 'TeamID'], how='left')
    else:
        print(f"No MasseyOrdinals file found at {ordinals_pattern}. Skipping NET/POM rankings.")
        for col in ['final_net', 'prev_net', 'net_improvement', 'final_pom', 'prev_pom', 'pom_improvement']:
            team_season_preds[col] = np.nan

    team_season_preds.dropna(inplace=True)
    return team_season_preds


def main():
    parser = get_parser()
    args = parser.parse_args()
    df = create_team_season_features(args.year, args.mode)

    file_path = f"{hf.get_generated_dir(args.year, args.mode)}/team_season_features.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
