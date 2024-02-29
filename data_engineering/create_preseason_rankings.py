from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import argparse
import helper_functions as hf
from constants import (
    CURRENT_YR,
    DATA_START_YR,
    GENERATED_DIR,
    GENERATED_DIR_LAST_YR,
)


def get_preseason_rankings(yr):
    link = f"https://www.espn.com/mens-college-basketball/rankings/_/week/1/year/{str(yr)}/seasontype/2"
    with urllib.request.urlopen(link) as url:
        page = url.read()
    soup = BeautifulSoup(page, "html.parser")
    rk_tables = soup.find_all("table", {"class": "Table"})
    # for some reason 2011 doesn't have an AP preseason poll
    # adding in logic to fall back on coaches poll instead
    if len(rk_tables[0].find_all("tr")) < 25:
        print(f"AP Top 25 not found for {yr}. Using Coaches Poll instead.")
        rk_table = rk_tables[1]
    else:
        rk_table = rk_tables[0]
    trs = rk_table.find_all("tr")
    cols = ["Season", "school", "preseason_pts"]
    preseason_rk_df = pd.DataFrame(columns=cols)
    for tr in trs[1:]:
        tds = tr.find_all("td")
        pts = int(tds[3].text)
        team = (
            tds[1].find("div").find("span").find("a").find("img").get("title").lower()
        )
        new_row = pd.DataFrame(columns=cols)
        new_row.loc[0] = [yr, team, pts]
        preseason_rk_df = pd.concat([preseason_rk_df, new_row], ignore_index=True)
    votes_text = soup.find("p", {"class": "TableDetails__Paragraph"}).text
    team_votes_str_lst = votes_text.split(":")[1].split(",")
    for team_vote_str in team_votes_str_lst:
        team_vote_lst = team_vote_str.split(" ")
        pts = int(team_vote_lst[len(team_vote_lst) - 1])
        team = " ".join(team_vote_lst[: len(team_vote_lst) - 1]).lower().strip()
        new_row = pd.DataFrame(columns=cols)
        new_row.loc[0] = [yr, team, pts]
        preseason_rk_df = pd.concat([preseason_rk_df, new_row], ignore_index=True)
    return preseason_rk_df


def get_all_preseason_rankings(
    end_year: int = CURRENT_YR, backfill: bool = False
) -> None:
    if backfill:
        preseason_rankings = get_preseason_rankings(DATA_START_YR)
        preseason_joined = hf.scraped_df_join_to_team_spellings(preseason_rankings)
        for yr in range(DATA_START_YR + 1, end_year + 1):
            # print(yr)
            new_preseason_rankings = get_preseason_rankings(yr)
            new_preseason_joined = hf.scraped_df_join_to_team_spellings(
                new_preseason_rankings
            )
            preseason_joined = pd.concat(
                [preseason_joined, new_preseason_joined], ignore_index=True
            )
            # print(check_for_missing_spellings(new_preseason_rankings, new_preseason_joined))
    else:
        preseason_rankings = get_preseason_rankings(end_year)
        preseason_joined = hf.scraped_df_join_to_team_spellings(preseason_rankings)
        preseason_rankings_historic = pd.read_csv(
            f"{hf.get_generated_dir(end_year - 1)}/preseason_rankings.csv"
        )
        preseason_joined = pd.concat(
            [preseason_joined, preseason_rankings_historic], ignore_index=True
        )
    preseason_joined.drop("TeamNameSpelling", axis=1, inplace=True)
    preseason_joined.to_csv(
        f"{hf.get_generated_dir(end_year)}/preseason_rankings.csv", index=False
    )


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Process preseason rankings.")

    # Add an argument for the backfill parameter
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Whether to backfill data or not. Defaults to False.",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function with the command-line arguments
    get_all_preseason_rankings(backfill=args.backfill)


if __name__ == "__main__":
    main()
