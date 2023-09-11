# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 22:22:08 2023

@author: veerg
"""

'''this code scrapes advanced statistical metrics from whoscored.com. It works by going to the
whoscored home page, and going through season by season to collect in-depth statistics for each team in 
each season'''

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
from constants import name_corrector as name_corrector
import pandas as pd
import numpy as np

whoscored = 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League'
data = pd.read_excel(PL_website_data)
data = data.drop(data.columns[0], axis = 1)



data['Home Team'] = data['Home Team'].apply(name_corrector)
data['Away Team'] = data['Away Team'].apply(name_corrector)
        
#driver = webdriver.Chrome(C_DRIVER_PATH)

driver = webdriver.Chrome(executable_path = C_DRIVER_PATH)

driver.get(whoscored)
driver.maximize_window()
time.sleep(5)

#making sure terms and conditions have been accepted
try:
    close_ad_button = driver.find_element(By.CLASS_NAME, 'webpush-swal2-close')
    close_ad_button.click()
except:
    pass
        
team_list = data['Home Team'].drop_duplicates()
team_list = team_list.tolist()
possession_by_season = {} #dictionary containing % of ball possession each team has per season
counter_attack_for_by_season = {} #dictionary containing % of goals scored by each team via counter attacks per season
counter_attack_against_by_season = {} #dictionary containing % of counter attack goals conceded by each team per season
open_play_for_by_season = {} #dictionary containing % of goals scored by each team via open play per season
open_play_against_by_season = {} #dictionary containing % of goals conceded by each team via open play per season



for season in full_seasons:
    
    '''these sub-dictionaries contain data for all teams for each season. 
    they are then added to the initial dictionary as values, with the keys being the seasons to which
    each sub-dictionary pertains '''
    
    season_possessions = {}
    counter_attacks_for = {}
    open_play_goals_for = {}
    counter_attacks_against = {}
    open_play_goals_against = {}
    
    #selecting season via dropdown menu
    dropdown = driver.find_element_by_id("seasons")
    dropdown.click()
    
    time.sleep(5)
    xpath = f".//*[contains(text(), '{season}')]"
    season_option = driver.find_element_by_xpath(xpath)
    season_option.click()
    time.sleep(2)
    
    #scraping statistics
    season_stats = driver.find_element_by_link_text("Team Statistics")
    season_stats.click()
    
    #moving to the statistics table
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4.3);")
    time.sleep(2)
    
    #scraping the table for possession stats
    stats_table = driver.find_element_by_id("top-team-stats-summary-content")
    rows = stats_table.find_elements_by_tag_name("tr")
    for row in rows:
        possession = row.find_element(By.CLASS_NAME, "possession   ")
        team = row.find_element(By.CLASS_NAME, "team-link")
        team_text = team.text
        team_text = team_text[3:]
        if team_text[0] == " ":
            team_text = team_text[1:]
        season_possessions[team_text] = float(possession.text)
    
    driver.execute_script("window.scrollTo(0, 0);")
    
    possession_by_season[season] = season_possessions
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2.4);")
    
    #scraping the goals info table for information on the types of goals teams score
    goals_for_info_table = driver.find_element(By.ID, "stage-goals-content")
    rows = goals_for_info_table.find_elements_by_tag_name("tr")
    for row in rows:
        attributes = row.find_elements(By.TAG_NAME, "td")
        team_text = attributes[1].text
        total_goals = 0
        for attribute in attributes[2:]:
            total_goals += float(attribute.text)
        counter_attack_goals = float(attributes[3].text)
        open_play_goals = float(attributes[2].text)
        
        ca_percentage = counter_attack_goals
        open_play_goals = open_play_goals
        
        open_play_goals_for[team_text] = open_play_goals/total_goals
        counter_attacks_for[team_text] = ca_percentage/total_goals
    
    
      
    
    counter_attack_for_by_season[season] = counter_attacks_for
    open_play_for_by_season[season] = open_play_goals_for
    
    #clicking on a button to display statistics regarding the types of goal each team concedes
    against_button = driver.find_element(By.LINK_TEXT, "Against")
    against_button.click()
    time.sleep(2)
    goals_against_info_table = driver.find_element(By.ID, "stage-goals-content")
    rows = goals_against_info_table.find_elements_by_tag_name("tr")
    
    #scraping the goals against table
    for row in rows:
        attributes_against = row.find_elements(By.TAG_NAME, "td")
        team_text = attributes_against[1].text
        total_goals = 0
        for attribute_against in attributes_against[2:]:
            total_goals += float(attribute_against.text)
        counter_attack_goals = float(attributes_against[3].text)
        open_play_goals = float(attributes_against[2].text)
        
        ca_percentage = counter_attack_goals
        open_play_goals = open_play_goals
        
        open_play_goals_against[team_text] = open_play_goals/total_goals
        counter_attacks_against[team_text] = ca_percentage/total_goals
    
    counter_attack_against_by_season[season] = counter_attacks_against
    open_play_against_by_season[season] = open_play_goals_against
    
    
    
        
'''          
print(possession_by_season)

print(counter_attack_for_by_season)
print("\n\n\n")
print(open_play_for_by_season)
print("\n\n\n\n\n\n\n\n")

print(counter_attack_against_by_season)
print("\n\n\n")
print(open_play_against_by_season)

'''

'''adding data to spreadsheet. Each row in the spreadsheet that has been loaded
pertains to a single game. The following code matches each game 
(using the season, home team, and away team) to the corresponding statistics and adds
the scraped statistics to the data table'''

#creating the lists that will later be used as new columns in the pandas dataframe
home_possession = []
away_possession = []
home_counter_attack_for = []
away_counter_attack_for = []
home_counter_attack_against = []
away_counter_attack_against = []
home_open_play_for = []
home_open_play_against = []
away_open_play_for = []
away_open_play_against = []


length = data.shape[0]
for i in range(length):
    season = data.iloc[i]['season'] 
    season_list = season.split("/")
    first_half = "20" + season_list[0]
    second_half = "20" + season_list[1]
    
    long_season = first_half + "/" + second_half
    
    #this code corrects a bug that was occuring for some unknown reason
    if long_season == "2019/20":
        long_season = "2019/2020"
    if long_season == "20/2021":
        long_season = "2020/2021"
    
    home_team = data.iloc[i]['Home Team']
    away_team = data.iloc[i]['Away Team']
    
    #for each match, the home/away teams and the season are used to match the teams to the data in the dictionaries
    home_counter_attack_for.append(counter_attack_for_by_season[long_season][home_team])
    away_counter_attack_for.append(counter_attack_for_by_season[long_season][away_team])
    home_counter_attack_against.append(counter_attack_against_by_season[long_season][home_team])
    away_counter_attack_against.append(counter_attack_against_by_season[long_season][away_team])
    home_open_play_for.append(open_play_for_by_season[long_season][home_team])
    away_open_play_for.append(open_play_for_by_season[long_season][away_team])
    home_open_play_against.append(open_play_against_by_season[long_season][home_team])
    away_open_play_against.append(open_play_against_by_season[long_season][away_team])
    
    home_possession.append(possession_by_season[long_season][home_team])
    away_possession.append(possession_by_season[long_season][away_team])

data['Home Counter Attack for factor'] = home_counter_attack_for
data['Away Counter Attack for factor'] = away_counter_attack_for
data['Home Counter Attack against factor'] = home_counter_attack_against
data['Away Counter Attack for factor'] = away_counter_attack_for

data['Home Open Play for factor'] = home_open_play_for
data['Away Open Play for factor'] = away_open_play_for
data['Home Open Play against factor'] = home_open_play_against
data['Away Open Play against factor'] = away_open_play_against

data['Home Possession'] = home_possession
data['Away Possession'] = away_possession

data.to_excel(WhoScored_data)



    
    
    
    
    
    
    
    
    