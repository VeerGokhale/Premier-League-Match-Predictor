# -*- coding: utf-8 -*-
'''this program incorporates betting odds into the backtested model predictions for the 
2022/2023 season to see if the model is able to deliver positive betting results. All the numbers
used (e.g the weekly returns, the expected values, etc.) assume the following:
    
you place a $1 bet on every game according to the advice of the model
(unless the model tells you not to bet because no option has an expected yield of more than $1)'''

import sys
sys.path.append(r'C:/Users/veerg/OneDrive/Documents/Premier League Predictor')
from constants import *
import numpy as np
import pandas as pd




'''these functions are used to convert the results column from 0,1,2 to Home Win, Draw, Away Win 
and the Correct Predictions column from 0/1 to Yes/No, just to make the final table more readable'''

def numToResult(num):
    if num == 0:
        return "Home Win"
    elif num == 1:
        return "Draw"
    elif num == 2:
        return "Away Win"
    else:
        return num
    
def binToYN(num):
    if num == 0:
        return "No"
    elif num == 1:
        return "Yes"
    else:
        return num

#betting_odds_data is a sheet found on Kaggle.
odds_df = pd.read_excel(betting_odds_data, usecols = [2,3,4,5,6])

#loading the model's predictions and applying the aforementioned functions to certain columns
last_season_predictions_df = pd.read_excel(last_season_predictions)
last_season_predictions_df = last_season_predictions_df.drop(last_season_predictions_df.columns[0], axis = 1)
last_season_predictions_df['Result'] = last_season_predictions_df['Result'].apply(numToResult)
last_season_predictions_df['Correct Prediction (Yes or No)'] = last_season_predictions_df['Correct Prediction (Yes or No)'].apply(binToYN)


#changing the names from the Kaggle spreadsheet to match the names used in this project
odds_df['HomeTeam'] = odds_df['HomeTeam'].apply(name_corrector)
odds_df['AwayTeam'] = odds_df['AwayTeam'].apply(name_corrector)



HomeEV = [] #the expected value of betting on a home win 
AwayEV = [] #the expected value of betting on an away win
DrawEV = [] #the expected value of betting on a draw
BestPick = [] #tells the user whether they should bet on a home win, a draw, an away win, or not at all
weeklyReturns = [] #how much money one makes from choosing the best pick 

for i in range(last_season_predictions_df.shape[0]):
    home_team = last_season_predictions_df.iloc[i]['Home Team']
    
    away_team = last_season_predictions_df.iloc[i]['Away Team']
    winProb = last_season_predictions_df.iloc[i]['Probability of Home Win']
    drawProb = last_season_predictions_df.iloc[i]['Probability of Draw']
    lossProb = last_season_predictions_df.iloc[i]['Probability of Away Win']
    result = last_season_predictions_df.iloc[i]["Result"]
    
    corresponding_df = odds_df[odds_df['HomeTeam'] == home_team]
    corresponding_df = corresponding_df[corresponding_df['AwayTeam'] == away_team]
    
    home_odds = corresponding_df.iloc[0]['B365H']
    draw_odds = corresponding_df.iloc[0]['B365D']
    away_odds = corresponding_df.iloc[0]['B365A']
    
    #expected value = return on result * probability of that result occurring
    home_ev = home_odds * winProb
    draw_ev = draw_odds * drawProb
    away_ev = away_odds * lossProb
    
    HomeEV.append(home_ev)
    AwayEV.append(away_ev)
    DrawEV.append(draw_ev)
    
    if max([home_ev, away_ev, draw_ev]) > 1: # a bet should only be placed if the expected return of that bet is more than $1
        if home_ev == max([home_ev, draw_ev, away_ev]):
            BestPick.append('Bet on Home Team')
            if result == "Home Win":
                weeklyReturns.append(home_odds)
            else:
                weeklyReturns.append(0)
        elif away_ev == max([home_ev, draw_ev, away_ev]):
            BestPick.append('Bet on Away Team')
            if result == "Away Win":
                weeklyReturns.append(away_odds)
            else:
                weeklyReturns.append(0)
        else:
            BestPick.append('Bet on Draw')
            if result == "Draw":
                weeklyReturns.append(draw_odds)
            else:
                weeklyReturns.append(0)
    else: #if no option has an expected return of more than $1, don't bet on it
        BestPick.append("Don't Bet on this game")
        weeklyReturns.append(1)

last_season_predictions_df['EV of Betting on Home'] = HomeEV
last_season_predictions_df['EV of Betting on Away'] = AwayEV
last_season_predictions_df['EV of Betting on Draw'] = DrawEV
last_season_predictions_df['Who to Bet on for this game?'] = BestPick
last_season_predictions_df['Actual Return on Recommended Bet'] = weeklyReturns

last_season_predictions_df.to_excel(betting_predictions)
#print(last_season_predictions_df)



totalReturns = sum(list(last_season_predictions_df['Actual Return on Recommended Bet']))

nine_mth_Return = (totalReturns - last_season_predictions_df.shape[0])/last_season_predictions_df.shape[0]
#total returns is the total money you'd have after placing all the recommended bets

print("Results of the Model, assuming you place allocate $1 to the model's betting recommendation for each game: \n")
print("Allocating $" + str(round((last_season_predictions_df.shape[0]),2)) +  
      " in total would yield $", round(totalReturns,2), ". So,the model yields a 9 month return of %"
      + str(100*round(nine_mth_Return,2)), 
      " ,which when annualized, comes out to %" + str(100*round((1+nine_mth_Return)**(12/9) - 1, 2))+ 
      " By comparison, the SnP 500 typically returns 5-10% every year.")


