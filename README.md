# March Madness Bracket Predictions
## Data Collection

High-level
- Run the following from the `data_engineering` directory.
- All data generated will write to the `data/[year]/` directory.
- To only generate data for this year and append it to last year's data, run the commands without the `--backfill` flag. This approach will be much faster and have less room for error. To re-generate/re-scrape data for all years including this one, use the `--backfill` flag.

Generating new data
- To generate preseason rankings data, run `python create_preseason_rankings.py [--backfill]`.
