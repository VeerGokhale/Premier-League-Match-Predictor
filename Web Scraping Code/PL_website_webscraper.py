# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 21:56:47 2023

@author: veerg
"""

'''this code scrapes the official premier league website
to create an excel file containing 
a list of all PL games within the relevant time period,
the season these games belong do, the date on which they were played,
the score, the home team, and the away team'''

import sys
sys.path.append(r'C:/Users/veerg/OneDrive/Documents/Premier League Predictor')
from constants import *
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from constants import name_corrector as name_corrector

scraped_data = pd.DataFrame(columns = pl_scraped_columns)
prem_results_page = "https://www.premierleague.com/results"


#ACCESSING PREMIER LEAGUE RESULTS WEBSITE

driver = webdriver.Chrome(C_DRIVER_PATH)
driver.get(prem_results_page)
driver.maximize_window()
time.sleep(2)


#accepting the terms and conditions of the website
try:
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
    )
    accept_button.click()
    
except:
    pass
    #print("Cannot access premier league website")

time.sleep(1.5)
#SELECTING THE LAST 11 Seasons by a CSS Field called "data-option-id"

testing_seasons_option_ids = ["21", "22", "27", "42", "54", "79", "210", "274", "363", "418", "489"]
match_counter = 0
for option_id in testing_seasons_option_ids:
    filter_season_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="mainContent"]/div[3]/div[1]/section/div[3]/div[2]'))
    )
    
    #selecting the correct season 
    filter_season_button.click()
    
    season_xpath_str = f"//*[@data-option-id='{option_id}']"

    time.sleep(1.5)
    
    
    season_select_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, season_xpath_str)))
    season = season_select_button.text
    season = season.replace("20", '')
    season_select_button.click()
    
    time.sleep(1.5)
    #the driver scrolls to the bottom so that the full page loads (the pauses are there to ensure full loading)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    
    #dividing the page into the tables that contain each invidual matchday
    fixture_container = driver.find_element_by_class_name("fixtures")
    matchday_containers = fixture_container.find_elements_by_class_name("fixtures__date-container")
    
    for matchday in matchday_containers[::-1]:
        #dividing each matchday table into the individual matchdays
        
        matches = matchday.find_elements_by_class_name("match-fixture")
        date_container = matchday.find_element_by_class_name("fixtures__date--long")
        date = date_container.text
        
        #extracting date, score, and team names from each match
        for match in matches[::-1]:
            team_list = []
            teams = match.find_elements_by_class_name("match-fixture__team-name")
            score_container = match.find_element_by_class_name("match-fixture__score")
            score = score_container.text
            score = (score.replace("\n", "")).split("-")
            for team in teams:
                team_list.append(team.text)
        
            
            #print(team_list[0] + " vs " + team_list[1] + ", " + date + ", " + score[0] + "-" + score[2])
            match_counter +=1
            
            scraped_data.loc[scraped_data.shape[0]] = [date, season, team_list[0], team_list[1], int(score[0]), int(score[1])]
            
            
                
    #scrolling back to the top of the page so a new season can be collected
    driver.execute_script("window.scrollTo(0, 0);")
            


#print(match_counter)

print("done \n")
print(scraped_data)

scraped_data.to_excel(PL_website_data)
driver.quit()
    
    
    
    
    
    

    



    
