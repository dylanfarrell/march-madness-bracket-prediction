import pandas as pd
from argparser_config import get_parser
import helper_functions as hf
from constants import GENERATED_DATASETS


def main():
    parser = get_parser()
    args = parser.parse_args()

    gold_data = hf.load_and_trim("MNCAATourneySeeds", 2003)[
        ["TeamID", "Season"]
    ].rename({"Season": "year"}, axis=1)
    print(len(gold_data))

    # Assuming GENERATED_DATASETS is a list of datasets to be loaded and merged
    if GENERATED_DATASETS:
        # Iterate over the remaining datasets and merge them with gold_data
        for i, dataset in enumerate(GENERATED_DATASETS):
            dataset = dataset + "_silver"
            suffixes = (f"_left_{i}", f"_right_{i}")
            print(suffixes)
            df = hf.load_silver_data(dataset, args.year)
            gold_data = pd.merge(
                gold_data,
                df,
                on=["TeamID", "year"],
                how="left",
                suffixes=suffixes,
            )
            print(f"{dataset} is complete.")

    print(gold_data.columns)

    file_path = f"{hf.get_gold_dir(args.year)}/gold_data_external_sources.csv"
    hf.write_to_csv(gold_data, file_path, args.overwrite)

    kaggle_features = hf.load_generated_data("team_season_features")
    gold_data_all = pd.merge(
        gold_data,
        kaggle_features,
        how="left",
        left_on=["TeamID", "year"],
        right_on=["TeamID", "Season"],
        suffixes=suffixes,
    )
    file_path = f"{hf.get_gold_dir(args.year)}/gold_data_all.csv"
    hf.write_to_csv(gold_data_all, file_path, args.overwrite)


if __name__ == "__main__":
    main()
