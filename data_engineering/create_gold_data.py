import pandas as pd
from argparser_config import get_parser
import helper_functions as hf
from constants import WOMENS_GENERATED_DATASETS, MENS_GENERATED_DATASETS, DATA_START_YR


def iteratively_join_data(
    df: pd.DataFrame, datasets: list[str], year: int, mode: str
) -> pd.DataFrame:
    for i, dataset in enumerate(datasets):
        dataset = dataset + "_silver"
        suffixes = (f"_left_{i}", f"_right_{i}")
        df = pd.merge(
            df,
            hf.load_silver_data(dataset, year, mode=mode),
            on=["TeamID", "year"],
            how="left",
            suffixes=suffixes,
        )
        print(f"{dataset} is complete.")
    return df


def main():
    parser = get_parser()
    args = parser.parse_args()
    mode = args.mode

    gold_data = hf.load_and_trim(f"{mode}NCAATourneySeeds", mode=mode)[
        ["TeamID", "Season"]
    ].rename({"Season": "year"}, axis=1)

    datasets = WOMENS_GENERATED_DATASETS if mode == "W" else MENS_GENERATED_DATASETS
    gold_data = iteratively_join_data(gold_data, datasets, args.year, mode)

    print(gold_data.columns)

    file_path = (
        f"{hf.get_gold_dir(args.year, mode=mode)}/gold_data_external_sources.csv"
    )
    hf.write_to_csv(gold_data, file_path, args.overwrite)

    # join features created from kaggle data to gold data
    kaggle_features = hf.load_generated_data("team_season_features", args.year, mode)
    gold_data_all = pd.merge(
        gold_data,
        kaggle_features,
        how="left",
        left_on=["TeamID", "year"],
        right_on=["TeamID", "Season"],
        suffixes=("_left", "_right"),
    )
    file_path = f"{hf.get_gold_dir(args.year, mode)}/gold_data_all.csv"
    hf.write_to_csv(gold_data_all, file_path, args.overwrite)


if __name__ == "__main__":
    main()
