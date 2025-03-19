import pandas as pd
import json
from argparser_config import get_parser
import helper_functions as hf


def create_model_data(year:int) -> pd.DataFrame:
  # read in gold data
  data = pd.read_csv(f"{hf.get_gold_dir(year)}/gold_data_all.csv")
  # read in feature metadata
  with open(f"{hf.get_gold_dir(year)}/data_dictionary.json",'rb') as f:
    metadata = json.load(f)
  
  id_cols = ['TeamID','team_name','Seed','Season']
  input_features = [k for k,v in metadata.items() if not v.get('exclude_from_model',False)]
  data = data[id_cols+input_features]

  # move to gold data creation
  data['preseason_pts'] = data['preseason_pts'].fillna(0)

  tourney_games = pd.read_csv(f'{hf.get_kaggle_dir(year)}/MNCAATourneyCompactResults.csv')
  tourney_games = tourney_games[tourney_games['Season'] >= data['Season'].min()].copy()
  tourney_games = tourney_games.merge(data, left_on=['Season', 'WTeamID'], right_on=['Season', 'TeamID'])\
  .merge(data, left_on=['Season', 'LTeamID'], right_on=['Season', 'TeamID'], suffixes=['_w', '_l'])
  winner_first = tourney_games.copy()
  winner_first['diff_score'] = winner_first['WScore'] - winner_first['LScore']
  loser_first = tourney_games.copy()
  loser_first['diff_score'] = loser_first['LScore'] - winner_first['WScore']
  for col in input_features:
      try:
          winner_first['diff_'+col] = winner_first[col+'_w'] - winner_first[col+'_l']
          loser_first['diff_'+col] = loser_first[col+'_l'] - loser_first[col+'_w']
      except:
          try:
            print(f'warning, converting {col} to float to calculate difference')
            winner_first['diff_'+col] = winner_first[col+'_w'].map(float) - winner_first[col+'_l'].map(float)
            loser_first['diff_'+col] = loser_first[col+'_l'].map(float) - loser_first[col+'_w'].map(float)
          except:
            print(f"Problem with {col}")

  model_data = pd.concat([winner_first,loser_first],ignore_index=True)

  return model_data


def main():
  # parse the command-line arguments
  parser = get_parser()
  args = parser.parse_args()
  table_name = 'model_data'
  df = create_model_data(args.year)

  # write the dataframe to a csv
  file_path = f"{hf.get_gold_dir(args.year)}/{table_name}.csv"
  hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
  main()
