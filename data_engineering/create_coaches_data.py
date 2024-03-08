import pandas as pd

import helper_functions as hf
from argparser_config import get_parsed_args
from constants import KAGGLE_DIR, SPORTS_REF_STUB


def create_coaches_data(year: int) -> pd.DataFrame:
    link = f"{SPORTS_REF_STUB}/cbb/seasons/{year}-coaches.html"
    soup = hf.get_soup(link, rate_limit=False)
    coach_table = soup.find("table", {"id": "coaches"})
    coach_tbody = coach_table.find("tbody")
    coach_rows = coach_tbody.find_all("tr")
    cols = [
        "Season",
        "school",
        "is_ap_pre_top_5",
        "is_ap_pre_top_15",
        "is_ap_pre_top_25",
        "coach_WL_car",
        "tourneys_car",
        "sw16_car",
        "ff_car",
        "champ_car",
    ]
    coach_df = pd.DataFrame(columns=cols)
    for coach_row in coach_rows:
        tds = coach_row.find_all("td")
        if len(tds) > 10:
            try:
                school = tds[0].find("a")["href"].split("/")[3]
                is_ap_pre_top_5 = False if tds[6].text == "" else int(tds[6].text) <= 5
                is_ap_pre_top_15 = (
                    False if tds[6].text == "" else 5 < int(tds[6].text) <= 15
                )
                is_ap_pre_top_25 = (
                    False if tds[6].text == "" else 15 < int(tds[6].text) <= 25
                )
                # arbitrarily choosing 0.300 winning % if the coach for some reason has no winning % listed (probably a bad sign)
                coach_WL_car = 0.3 if tds[21].text == "" else float(tds[21].text)
                tourneys_car = 0 if tds[22].text == "" else int(tds[22].text)
                sw16_car = 0 if tds[23].text == "" else int(tds[23].text)
                ff_car = 0 if tds[24].text == "" else int(tds[24].text)
                champ_car = 0 if tds[25].text == "" else int(tds[25].text)
                new_row = pd.DataFrame(columns=cols)
                new_row.loc[0] = [
                    year,
                    school,
                    is_ap_pre_top_5,
                    is_ap_pre_top_15,
                    is_ap_pre_top_25,
                    coach_WL_car,
                    tourneys_car,
                    sw16_car,
                    ff_car,
                    champ_car,
                ]
                coach_df = pd.concat([coach_df, new_row], ignore_index=True)
            except:
                print(f"Skip bad row: {tds[0]}")
    return coach_df


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

    # Call the function with the command-line arguments
    df = create_coaches_data(year=args.year)
    file_path = f"{hf.get_generated_dir(args.year)}/coaches_data.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
