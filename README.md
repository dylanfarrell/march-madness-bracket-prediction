# march-madness-bracket-prediction

## Data Collection
Run the following from the `data_engineering` directory. All data generated will write to the `data/[year]/` directory.
- To generate preseason rankings data, run `python create_preseason_rankings.py`. This will append the newest year's data to last year's data.
  - To generate and rescrape all preseason rankings data, run `python create_preseason_rankings.py --backfill`.
