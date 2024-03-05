with season_stats_join as (
    select
        *
    from {{ ref("regular_season_winning_team_results")}} as w
    full outer join {{ ref("regular_season_losing_team_results")}} as l
    on w.Season = l.Season and w.TeamID = l.TeamID
)
select
    *,
    num_wins + num_losses as total_games,
    sum_score_w + sum_score_l
from season_stats_join


# total games
team_season_stats['total_games'] = team_season_stats['num_wins'] + team_season_stats['num_losses']

# total points for
team_season_stats['total_points_for'] = team_season_stats['sum_score_w'] + team_season_stats['sum_score_l']

# total points against
team_season_stats['total_points_against'] = team_season_stats['sum_score_of_opponents_w'] + team_season_stats['sum_score_of_opponents_l']

# win pct.
team_season_stats['win_pct'] = team_season_stats['num_wins'] / team_season_stats['total_games']

# avg. points for
team_season_stats['avg_points_for'] = team_season_stats['total_points_for'] / team_season_stats['total_games']

# avg. points against
team_season_stats['avg_points_against'] = team_season_stats['total_points_against'] / team_season_stats['total_games']

# 3FGA per game
team_season_stats['3FGA_pg'] = (team_season_stats['sum_3FGA_w'] + team_season_stats['sum_3FGA_l']) / team_season_stats['total_games']

# 3FGM per game
team_season_stats['3FGM_pg'] = (team_season_stats['sum_3FGM_w'] + team_season_stats['sum_3FGM_l']) / team_season_stats['total_games']

# 3 pt. pct.
team_season_stats['3_pct'] = team_season_stats['3FGM_pg'] / team_season_stats['3FGA_pg']

# FTA per game
team_season_stats['FTA_pg'] = (team_season_stats['sum_FTA_w'] + team_season_stats['sum_FTA_l']) / team_season_stats['total_games']

# FTM per game
team_season_stats['FTM_pg'] = (team_season_stats['sum_FTM_w'] + team_season_stats['sum_FTM_l']) / team_season_stats['total_games']

# FT pct.
team_season_stats['FT_pct'] = team_season_stats['FTM_pg'] / team_season_stats['FTA_pg']

# TOV per game
team_season_stats['TOV_pg'] = (team_season_stats['sum_TOV_w'] + team_season_stats['sum_TOV_l']) / team_season_stats['total_games']

# turn strings of winning and losing margins into one tuple
team_season_stats['differential_arr'] = [literal_eval(wm + ',' + lm) for wm, lm in zip(team_season_stats['winning_margins'], team_season_stats['losing_margins'])]

# avg. score differential
team_season_stats['avg_game_margin'] = [np.mean(arr) for arr in team_season_stats['differential_arr']]

# std. dev. of score differential
team_season_stats['std_game_margin'] = [np.std(arr) for arr in team_season_stats['differential_arr']]

# avg. pace
team_season_stats['avg_pace'] = (team_season_stats['sum_pace_w'] + team_season_stats['sum_pace_l']) / team_season_stats['total_games']

# avg. off. efficiency
team_season_stats['off_eff'] = (team_season_stats['sum_off_eff_w'] + team_season_stats['sum_off_eff_l']) / team_season_stats['total_games']

# avg. def. efficiency
team_season_stats['def_eff'] = (team_season_stats['sum_def_eff_w'] + team_season_stats['sum_def_eff_l']) / team_season_stats['total_games']

# pythagorean win pct. (Morey version: k=13.91)
k = 13.91
team_season_stats['pythag_win_pct'] = (team_season_stats['total_points_for'] ** k) / \
    (team_season_stats['total_points_for'] ** k + team_season_stats['total_points_against'] ** k)

# luck
team_season_stats['luck'] = team_season_stats['win_pct'] - team_season_stats['pythag_win_pct']