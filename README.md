# March Madness Bracket Predictions
## Data Collection

**High-level**
- Run the following from the `data_engineering` directory.
- Run `./create_data_directories.sh [year]` first to get necessary directories in place.
- All data generated will write to the `data/[year]/` directory above.
- To only generate data for this year and append it to last year's data, run the commands without the `--recompute` flag. This approach will be much faster and have less room for error. To recompute/re-scrape data for all years including this one, use the `--recompute` flag.
  - For example, if you wanted to generate data for 2024 with all years recomputed/re-scraped: `python [file].py --year=2024 --recompute`.
  - If you wanted to generate data for 2023 by only computing the newest year of data: `python [file].py --year=2023`.
  - Upon receiving the kaggle data, run `python team_spellings_helpers.py --year=[year] --overwrite` to update the `MTeamSpellings` table with old manually added team spellings.

**Generating new raw data**
- Note: For the following, if a data directory isn't already in place for the past year, you'll have to add the `--recompute` flag to scrape all past years of data as well as this year.
- The first script to run is `python create_sports_reference_team_data.py [--year]`
  - This will create a pickled dataset of all of the D1 NCAA basketball teams from sports reference. A lot of other models rely on this list to loop through, so it should be first. If this dataset doesn't exist, functions requiring a list of teams will fall back onto last year's team, which could cause problems if the set of D1 teams has changed.
  - This will also scrape some basic team statistics for each team.
- To generate preseason rankings data, run `python create_preseason_rankings_data.py --year=[year]`.
- To generate coaching data, run `python create_coaches_data.py --year=[year]`.
- To generate coaching data, run `python create_returning_player_team_data.py --year=[year] --tourney_teams_only`. The `--tourney_teams_only` flag will only compute this for teams that made the NCAA tournament, cutting runtime from ~20 min --> ~4 min.
- To generate coaching data, run `python create_weighted_player_data.py --year=[year] --tourney_teams_only`. The `--tourney_teams_only` flag will only compute this for teams that made the NCAA tournament, cutting runtime from ~20 min --> ~4 min.

**Generating "silver" data**
- The above tables are disentangled from kaggle data as much as possible (with the exception of the `--tourney_teams_only` data, although omitting this flag disentangles it entirely from kaggle data). This is to allow the above to be run before the kaggle data is released for a given year. If we consider the above data "bronze" data, this is "silver" data. It is the same as the above data with kaggle ids joined to it.
- Run `python create_silver_data.py --year=[year]`.
- Teams that can't find matching kaggle ids will be dropped and logged to the console. We will deal with these later.
- All datasets will be written to the `silver_data` directory.

**Generating "gold" data**
- At this step we combine our silver data with features derived from kaggle to put into one clean dataset -- this is the data used for training our model in downstream consumption.
- Run `python create_gold_data.py --year=[year]`.
