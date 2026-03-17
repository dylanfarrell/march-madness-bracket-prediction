import pandas as pd
from argparser_config import get_parser
import helper_functions as hf


def create_seeds_json(year:int, mode:str) -> pd.DataFrame:

  seeds = pd.read_csv(f"{hf.get_kaggle_dir(year, mode)}/{mode}NCAATourneySeeds.csv")
  seeds=seeds[seeds['Season']==year]
  gold_data = pd.read_csv(f'{hf.get_gold_dir(year, mode)}/gold_data_all.csv')
  gold_data = gold_data[gold_data['year']==year]
  seeds = seeds.merge(gold_data[['TeamID','team_left_1','team_name']],on='TeamID')
  seeds['sr_name'] = seeds['team_left_1']
  seeds = seeds[['Seed','TeamID','sr_name','team_name']]
  seeds.set_index('Seed',inplace=True)
  return seeds

def main():
  # parse the command-line arguments
  parser = get_parser()
  args = parser.parse_args()
  df = create_seeds_json(args.year, args.mode)

  # write the dataframe to a csv
  file_path = f"{hf.get_gold_dir(args.year, args.mode)}/seeds.json"
  df.to_json(file_path,orient='index',indent=4)

if __name__ == "__main__":
  main()