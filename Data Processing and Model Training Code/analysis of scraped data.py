# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 20:43:05 2023

@author: veerg
"""

'''this file combines the data scraped from the Premier League and Whoscored websites
with the data scraped from transfermarkt and the starting xis to produce a dataset
that also contains the transfer values of both the home and away teams starting xis.

Moreover, the following form-based metrics are also added using the available data (for both the home and away teams):
    
    PPG : points per game 
    GFPG: goals for per game 
    GAPG: goals against per game
    
To calculate this, a lookback period of 5 games was applied. If not enough games had elapsed
for there to be a 5 game lookback period, the games were dropped from the dataset.

Note: where necessary, data from previous seasons was allowed to be used to calculate these form-based metrics
for early season entries

Note: for the home team, I used that teams last 5 HOME GAMES ONLY to work out these metrics
(and vice versa for the away team). 



'''

import sys
sys.path.append(r'C:/Users/veerg/OneDrive/Documents/Premier League Predictor')
from constants import *
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from constants import who_scored_season_shortener
from constants import name_corrector as name_corrector
import pandas as pd
import numpy as np
import json
import ast

import copy

#loading data

data = pd.read_excel(WhoScored_data)
data = data.drop([data.columns[0], data.columns[1]], axis = 1)
data['season'] = data['season'].apply(season_corrector) 




# Load dictionary from a JSON file
with open(transfer_value_data, 'r') as f:
    transfer_vals = json.load(f)

starting_XIs = pd.read_excel(starting_xi_data)

starting_XIs = starting_XIs.drop(starting_XIs.columns[0], axis = 1)
starting_XIs['Season'] = starting_XIs['Season'].apply(who_scored_season_shortener)

#adding starting xi transfer values
home_transfer_val_column = []
away_transfer_val_column = []

for i in range(data.shape[0]):
    season = data.iloc[i]['season']
    home_team = data.iloc[i]['Home Team']
    away_team = data.iloc[i]['Away Team']
    
    
    correct_season = starting_XIs[starting_XIs['Season'] == season]
    correct_season_home = correct_season[correct_season['Home Team'] == home_team]
    correct_row = correct_season_home[correct_season_home['Away Team'] == away_team]
    
    #the ast.literal_eval is used to transform the excel data from string to list
    home_xi = ast.literal_eval(correct_row.iloc[0]['Home Team XI'])
    away_xi = ast.literal_eval(correct_row.iloc[0]['Away Team XI'])
    
    '''these dicts contain the transfer values of every player in a team
    from the given season'''
    
    home_team_dict = transfer_vals[home_team][season]
    away_team_dict = transfer_vals[away_team][season]
    
    home_values = 0
    away_values = 0
    
    '''when looping through the starting xis and adding the corresponding transfer values
    from the dictionary, we must keep in mind that the transfer value dictionary contains
    full names of players, but the starting xi data only has their last names
    
    --> we must check to see if the names from the starting_xi dictionary are present in the
    dictionary keys as opposed to being equal to them
    
    '''
    
    for home_player in home_xi:
        for key in home_team_dict.keys(): 
            if home_player in key: 
                home_values += home_team_dict[key]
    for away_player in away_xi:
        for key in away_team_dict.keys():
            if away_player in key:
                away_values += away_team_dict[key]
    home_transfer_val_column.append(home_values)
    away_transfer_val_column.append(away_values)
    
data['Home Transfer Value'] = home_transfer_val_column
data['Away Transfer Value'] = away_transfer_val_column    

#adding form metrics

'''the first game in the dataset is filled with 0s for the form metrics since they cannot be calculated
and attempting to do so will break the code. The first game in the dataset will be removed anyway'''

#all these lists are later turned into df columns

home_GFPG = [0]
home_GAPG = [0]
away_GFPG = [0]
away_GAPG = [0]
home_PPG = [0]
away_PPG = [0]
keep_row = [0] #a 0 in this column means the row will later be removed. A 1 means it will be kept


num_rows = data.shape[0]

#this variable can be modified to change the form lookback period
form_lookback = 5

for i in range(1,num_rows):
    keep = 1
    home_team = data.loc[i]['Home Team']
    away_team = data.loc[i]['Away Team']
    
    #only consider previous data
    reduced_data = data.iloc[:i]
    
    #working out home PPG
    #we only want to use games where the current home team was also playing at home
    home_team_only = reduced_data[reduced_data['Home Team'] == home_team]
    

    if home_team_only.shape[0] < form_lookback: #if there isn't enough data to calculate the metrics
        home_PPG.append(0)
        home_GFPG.append(0)
        home_GAPG.append(0)
        keep = 0
    else:
        relevant_home_games = home_team_only.iloc[home_team_only.shape[0]-form_lookback :]
        points = 0
        home_GF = 0
        home_GA = 0
        for j in range(form_lookback):
            if relevant_home_games.iloc[j]['Home Team Score'] > relevant_home_games.iloc[j]['Away Team Score']:
                points +=3 #if the home team won
            elif relevant_home_games.iloc[j]['Home Team Score'] == relevant_home_games.iloc[j]['Away Team Score']:
                points +=1 #if the home team drew
            else:
                points +=0 #if the home team lost
            
            home_GF += relevant_home_games.iloc[j]['Home Team Score']
            home_GA += relevant_home_games.iloc[j]['Away Team Score']
        
        
        ppg = points/form_lookback #dividing by lookback to make it "per game"
        
        home_GFPG.append(home_GF/form_lookback)
        home_GAPG.append(home_GA/form_lookback)
        home_PPG.append(ppg)
        
    
    #methodology for away team calculations is exactly the same as that of the home team
    
    away_team_only = reduced_data[reduced_data['Away Team'] == away_team]
    if away_team_only.shape[0] < form_lookback:
        away_PPG.append(0)
        keep = 0
        away_GFPG.append(0)
        away_GAPG.append(0)
    else:
        relevant_away_games = away_team_only.iloc[away_team_only.shape[0]-form_lookback :]
        points = 0
        away_GF = 0
        away_GA = 0
        for j in range(form_lookback):
            if relevant_away_games.iloc[j]['Away Team Score'] > relevant_away_games.iloc[j]['Home Team Score']:
                points +=3
            elif relevant_away_games.iloc[j]['Away Team Score'] == relevant_away_games.iloc[j]['Home Team Score']:
                points +=1
            else:
                points +=0
            
            away_GF += relevant_away_games.iloc[j]['Away Team Score']
            away_GA += relevant_away_games.iloc[j]['Home Team Score']
            
        away_GFPG.append(away_GF/form_lookback)
        away_GAPG.append(away_GA/form_lookback)
        ppg = points/form_lookback
        away_PPG.append(ppg)
    
    keep_row.append(keep)

#setting new columns 

data['Home Team Home PPG'] = home_PPG
data['Away Team Away PPG'] = away_PPG
data['Home Team Home GFPG'] = home_GFPG
data['Away Team Away GFPG'] = away_GFPG
data['Home Team Home GAPG'] = home_GAPG
data['Away Team Away GAPG'] = away_GAPG

data['keep row?'] = keep_row

data.to_excel(final_data)        
    
        



