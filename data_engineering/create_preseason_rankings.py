import pandas as pd

import helper_functions as hf
from argparser_config import get_parsed_args


def get_preseason_rankings(year: int) -> pd.DataFrame:
    link = f"https://www.espn.com/mens-college-basketball/rankings/_/week/1/year/{year}/seasontype/2"
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
    cols = ["season", "team", "preseason_pts"]
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
    # Parse the command-line arguments
    args = get_parsed_args()

    df = hf.generate_data_all_years(
        get_preseason_rankings,
        year=args.year,
        recompute=args.recompute,
        table_name="preseason_rankings",
    )

    # Call the function with the command-line arguments
    file_path = f"{hf.get_generated_dir(args.year)}/preseason_rankings.csv"
    hf.write_to_csv(df, file_path, args.overwrite)


if __name__ == "__main__":
    main()
