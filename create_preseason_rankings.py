from bs4 import BeautifulSoup
import urllib.request
import numpy as np
import pandas as pd


def get_preseason_rankings(yr):
    link = (
        "https://www.espn.com/mens-college-basketball/rankings/_/week/1/year/"
        + str(yr)
        + "/seasontype/2"
    )
    with urllib.request.urlopen(link) as url:
        page = url.read()
    soup = BeautifulSoup(page, "html.parser")
    rk_table = soup.find("table", {"class": "Table"})
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
