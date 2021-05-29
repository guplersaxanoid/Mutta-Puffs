import pandas as pd
import numpy as np 
import dataframe_image as dfi

def get_teams(filename):
    teams = []
    with open(filename,"r") as f:
        for line in f:
            if len(line) != 0:
                teams.append(line.strip().split(":"))
    return teams

def process_schedule(S, teams):
    proceessed_S = np.zeros(S.shape, dtype=object)
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            team = teams[abs(S[i][j])-1][1]
            if S[i][j] < 0:
                team = '@'+team 
            proceessed_S[i][j] = team 
    return proceessed_S

def get_schedule(filename):
    S = []
    with open(filename,"r") as f:
        for line in f:
            S.append([int(x) for x in line.strip().split()])
    return np.array(S)

def generate_schedule_table():
    teams = get_teams('input/teams.txt')
    S = process_schedule(get_schedule("input/s0.txt"), teams)
    #print(S)
    table = {}
    for i in range(S.shape[1]):
        table[f'week {i+1}'] = S[:,i]
    df = pd.DataFrame(table)
    team_col = []
    for team in teams:
        team_col.append(f"{team[0]} ({team[1]})")
    df.index = team_col
    return df 

S = generate_schedule_table()
dfi.export(S,'schedule.png')