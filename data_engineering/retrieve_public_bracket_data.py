import pandas as pd
from pandasql import sqldf
import helper_functions as hf


def scrape_public_bracket(year: int) -> pd.DataFrame:
    link = (
        f"https://fantasy.espn.com/tournament-challenge-bracket/{year}/en/whopickedwhom"
    )
    soup = hf.get_soup(link)
    wpw_table = soup.find("table", {"class": "wpw-table"})
    cols = ["year", "team", "pct"]
    team_pcts = pd.DataFrame(columns=cols)
    trs = wpw_table.find_all("tr")
    for tr in trs[1:]:
        tds = tr.find_all("td")
        for td in tds:
            team = td.find("span", {"class": "teamName"}).text.lower()
            pct = float(td.find("span", {"class": "percentage"}).text.rstrip("%"))
            new_row = pd.DataFrame(columns=cols)
            new_row.loc[0] = [year, team, pct]
            team_pcts = pd.concat([team_pcts, new_row], ignore_index=True)
    q = """
    SELECT
        yr,
        school, 
        pct AS pct_win_rd,
        ROW_NUMBER() OVER(PARTITION BY school ORDER BY pct DESC) rd
    FROM team_pcts
    """
    team_pct_by_rd = sqldf(q)
    return team_pct_by_rd
