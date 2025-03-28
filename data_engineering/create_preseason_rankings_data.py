import pandas as pd

import helper_functions as hf
from argparser_config import get_parser
from constants import MODE_DIRECTORY


def get_preseason_rankings(year: int, mode: str) -> pd.DataFrame:
    mode = MODE_DIRECTORY[mode]
    link = f"https://www.espn.com/{mode}-college-basketball/rankings/_/week/1/year/{year}/seasontype/2"
    soup = hf.get_soup(link)
    rk_tables = soup.find_all("table", {"class": "Table"})
    # for some reason 2011 doesn't have an AP preseason poll
    # adding in logic to fall back on coaches poll instead
    if len(rk_tables[0].find_all("tr")) < 25:
        print(f"AP Top 25 not found for {year}. Using Coaches Poll instead.")
        rk_table = rk_tables[1]
    else:
        rk_table = rk_tables[0]
    trs = rk_table.find_all("tr")
    cols = ["year", "team", "preseason_pts"]
    preseason_rk_df = pd.DataFrame(columns=cols)
    for tr in trs[1:]:
        tds = tr.find_all("td")
        pts = int(tds[3].text)
        team = (
            tds[1].find("div").find("span").find("a").find("img").get("title").lower()
        )
        new_row = pd.DataFrame(columns=cols)
        new_row.loc[0] = [year, team, pts]
        preseason_rk_df = pd.concat([preseason_rk_df, new_row], ignore_index=True)
    votes_text = soup.find("p", {"class": "TableDetails__Paragraph"}).text
    team_votes_str_lst = votes_text.split(":")[1].split(",")
    for team_vote_str in team_votes_str_lst:
        team_vote_lst = team_vote_str.split(" ")
        pts = int(team_vote_lst[len(team_vote_lst) - 1])
        team = " ".join(team_vote_lst[: len(team_vote_lst) - 1]).lower().strip()
        new_row = pd.DataFrame(columns=cols)
        new_row.loc[0] = [year, team, pts]
        preseason_rk_df = pd.concat([preseason_rk_df, new_row], ignore_index=True)
    return preseason_rk_df


def main():
    # parse the command-line arguments
    parser = get_parser()
    args = parser.parse_args()

    table_name = "preseason_rankings"

    # call the function with the command-line arguments
    df = hf.generate_data_all_years(
        get_preseason_rankings,
        year=args.year,
        mode=args.mode,
        recompute=args.recompute,
        table_name=table_name,
    )

    # write the dataframe to a csv
    file_path = f"{hf.get_generated_dir(args.year, args.mode)}/{table_name}.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
