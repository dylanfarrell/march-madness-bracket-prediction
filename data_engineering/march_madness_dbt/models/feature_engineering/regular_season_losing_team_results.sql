select 
    Season, 
    LTeamID AS TeamID, 
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
from {{ ref('regular_season_detailed_results_full') }}
group by 1, 2