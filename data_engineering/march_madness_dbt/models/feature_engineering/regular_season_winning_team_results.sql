
-- Use the `ref` function to select from other models

select
    Season, 
    WTeamID AS TeamID, 
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
from {{ ref('regular_season_detailed_results_full') }}
group by 1, 2
