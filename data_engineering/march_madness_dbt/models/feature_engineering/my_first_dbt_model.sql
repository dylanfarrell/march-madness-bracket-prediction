{{ config(materialized='table') }}

/*
This model derives new team game statistics. Columns include:
    - WPos: winning team possessions
    - LPos: losing team possessions
    - Pace: pace of the game
    - WOffEff: winning team offensive efficiency
    - LOffEff: losing team offensive efficiency

    Calculations are taken from https://www.nbastuffer.com/analytics101/
*/

with regular_season_detailed_results as (
    select 
    *,
    0.96 * (WFGA + WTO + 0.44 * WFTA - WOR) as WPos,
    0.96 * (LFGA + LTO + 0.44 * LFTA - LOR) as LPos
    from {{ source('my_source','regular_season_detailed_results') }}
)
select 
    *,
    (200 / (200 + 5 * 5 * NumOT)) * (WPos + LPos) / 2 as Pace,
    100 * (WScore / WPos) as WOffEff,
    100 * (LScore / LPos) as LOffEff
from regular_season_detailed_results
