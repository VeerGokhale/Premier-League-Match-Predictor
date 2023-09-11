# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 23:35:56 2023

@author: veerg
"""

from pathlib import Path
#This file contains important variables and functions that have uses across multiple files

#important variables
C_DRIVER_PATH = r"C:\Program Files (x86)\chromedriver.exe"
pl_scraped_columns = ['Date', 'season','Home Team', 'Away Team', 'Home Team Score', 'Away Team Score']
seasons = ["12/13","13/14","14/15","15/16","16/17","17/18","18/19", "19/20", "20/21", "21/22", "22/23"]
full_seasons = ["2012/2013", "2013/2014", "2014/2015", "2015/2016", "2016/2017", "2017/2018","2018/2019", "2019/2020", "2020/2021", "2021/2022", "2022/2023"]

#file_paths
root_directory = Path(__file__).parent


PL_website_data = root_directory / "Data" / "Prem Website Scraped Data.xlsx"
WhoScored_data = root_directory / "Data"/"WhoScored scraped data.xlsx"
starting_xi_data = root_directory / "Data" / "starting XIs.xlsx"
transfer_value_data = root_directory / "Data" / "player transfer values.json"
final_data = root_directory / "Data" / "final data.xlsx"
last_season_predictions = root_directory / "Data" /'Last Season Predictions.xlsx'
betting_odds_data = root_directory/ "Data" / 'Betting Odds.xlsx'
betting_predictions = root_directory / "Data" / "Predictions with Betting Odds"




def name_corrector(team):
    #this function standardizes the names because each site labels different teams slightly differently
    if team == "Man Utd":
        return "Manchester United"
    elif team == "Man City":
        return "Manchester City"
    elif team == "Spurs":
        return "Tottenham"
    elif team == "Sheffield Utd":
        return "Sheffield United"
    elif team == "WBA":
        return "West Bromwich Albion"
    elif team == "West Brom":
        return "West Bromwich Albion"
    elif team == "QPR":
        return "Queens Park Rangers"
    elif team == "Nott'm Forest":
        return "Nottingham Forest"
    elif team == "Sheff Utd":
        return "Sheffield United"
    elif team == "Man United":
        return "Manchester United"
    else: 
        return team

def transfer_vals_func(tval):
    if tval == None:
        return 0
    new_val = tval.replace("€", "")
    new_val = new_val.replace(" ", "")
    if (new_val == ""):
        return 0
    last_char = new_val[len(new_val) - 1]
    if last_char == "k":
        new_val = new_val.replace("k", "")
        return float(int(new_val)/1000)
    elif last_char == "m":
        new_val = new_val.replace("m", "")
        new_val = float(new_val)
        return new_val
    else:
        return 0
    

def season_corrector(season):
    if season[0] == "/":
        last_half = int(season[1:])
        first_half = str(last_half - 1)
        return first_half + season
    
    elif season[(len(season))-1] == '/':
        first_half = int(season[:2])
        second_half = str(first_half + 1)
        return season + second_half
    else:
        return season
    

def who_scored_season_shortener(season):
    season_halves = season.split("/")
    first_half = season_halves[0][2:]
    second_half = season_halves[1][2:]
    return (first_half+"/"+second_half)

    


    
    
        