import pandas as pd
from argparser_config import get_parser
import helper_functions as hf
from itertools import combinations
import json

def create_bracket_data(year:int) -> pd.DataFrame:

  seeds = pd.read_csv(f"{hf.get_kaggle_dir(year)}/MNCAATourneySeeds.csv")
  seeds=seeds[seeds['Season']==2024]
  gold_data = pd.read_csv(f'{hf.get_gold_dir(year)}/gold_data_all.csv')
  gold_data = gold_data[gold_data['year']==2024]

  with open(f"{hf.get_gold_dir(year)}/data_dictionary.json",'rb') as f:
    metadata = json.load(f)
  
  input_features = [k for k,v in metadata.items() if not v.get('exclude_from_model',False)]

  # get all two-pair combinations of column 'A' as a list
  combos = list(combinations(seeds['TeamID'], 2))

  unique_pairs = set(frozenset(pair) for pair in combos)

  # create a new dataframe from the combinations list
  combo_df = pd.DataFrame(unique_pairs, columns=['team1', 'team2'])
  combo_df = combo_df[combo_df['team1'] != combo_df['team2']]
  combo_df['Season']=2024

  # 2023 matchups
  bracket_data = combo_df.merge(gold_data, left_on=['Season', 'team1'], right_on=['Season', 'TeamID'])\
  .merge(gold_data, left_on=['Season', 'team2'], right_on=['Season', 'TeamID'], suffixes=['_1', '_2'])

  for col in input_features:
      try:
          bracket_data['diff_'+col] = bracket_data[col+'_1'] - bracket_data[col+'_2']
      except:
          bracket_data['diff_'+col] = bracket_data[col+'_1'].map(float) - bracket_data[col+'_2'].map(float)
  diff_cols = [col for col in bracket_data.columns if 'diff' in col]
  matchup_cols = ['Season', 'TeamID_1', 'TeamID_2','team_name_1','team_name_2', 'Seed_1', 'Seed_2'] + diff_cols
  bracket_data = bracket_data[matchup_cols]
  return bracket_data
  
def main():
  # parse the command-line arguments
  parser = get_parser()
  args = parser.parse_args()
  df = create_bracket_data(args.year)

  # write the dataframe to a csv
  file_path = f"{hf.get_gold_dir(args.year)}/bracket_data.csv"
  hf.write_to_csv(df, file_path, args.overwrite)

if __name__ == "__main__":
  main()
