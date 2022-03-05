def team_lookup(id_num, teams):
    return(teams[teams['TeamID'] == id_num]['TeamName'].values[0])