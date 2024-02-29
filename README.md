# March Madness Bracket Predictions
## Data Collection

**High-level**
- Run the following from the `data_engineering` directory.
- All data generated will write to the `data/[year]/` directory.
- To only generate data for this year and append it to last year's data, run the commands without the `--backfill` flag. This approach will be much faster and have less room for error. To recompute/re-scrape data for all years including this one, use the `--backfill` flag.
  - For example, if you wanted to generate data for 2024 with all years recomputed/re-scraped: `python [file].py [--year 2024] --backfill`.
  - If you wanted to generate data for 2021 by only compute the newest year of data: `python [file].py --year 2021`.

**Generating new data**
- To generate preseason rankings data, run `python create_preseason_rankings.py [--backfill]`.
