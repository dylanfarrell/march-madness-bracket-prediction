import re
import time
import urllib.request

from bs4 import BeautifulSoup
import pandas as pd

from argparser_config import get_parsed_args
import helper_functions as hf
from constants import SPORTS_REF_STUB


def get_returning_player_team_info(yr):
    link = f"{SPORTS_REF_STUB}/cbb/seasons/{yr}-coaches.html"
    soup = hf.get_soup(link)

    coach_table = soup.find("table", {"id": "coaches"})
    coach_tbody = coach_table.find("tbody")
    coach_rows = coach_tbody.find_all("tr")

    coach_rows_lst = []
    for coach_row in coach_rows:
        tds = coach_row.find_all("td")
        # some rows with minimal tds are not actual data rows
        if len(tds) > 10:
            team_stub = tds[0].find("a")["href"]
            school = team_stub.split("/")[3]
            team_link = f"{SPORTS_REF_STUB}{team_stub}"
            print(school)
            with urllib.request.urlopen(team_link) as url:
                page = url.read()
                # sports reference has a limit of 20 requests per minute
                # limiting to 15 requests to be safe
                time.sleep(4)
            team_soup = BeautifulSoup(page, "html.parser")
            text_div = team_soup.find("div", {"id": "tfooter_roster"}).text
            decimals = re.findall("\d+\.\d", text_div)
            returning_min_pct = float(decimals[0])
            returning_score_pct = float(decimals[1])
            row = [yr, school, returning_min_pct, returning_score_pct]
            coach_rows_lst.append(row)
    cols = ["Season", "school", "returning_min_pct", "returning_score_pct"]
    return pd.DataFrame(data=coach_rows_lst, columns=cols)


def main():
    # Parse the command-line arguments
    args = get_parsed_args()

    # Call the function with the command-line arguments
    df = get_returning_player_team_info(yr=args.year)
    df.to_csv(f"{hf.get_generated_dir(args.year)}/preseason_rankings.csv")


if __name__ == "__main__":
    main()
