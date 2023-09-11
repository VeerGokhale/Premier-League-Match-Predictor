# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 19:14:55 2023

@author: veerg
"""
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
from selenium.webdriver.chrome.options import Options
from constants import name_corrector as name_corrector
import pandas as pd
import numpy as np
'''This scraper works slightly differently to the rest. First, it goes on whoscored.com,
and accesses every Premier League result from the specified time period. It then appends the
links to the in-depth information from these games to a list, called "links". After all the matches'
corresponding links have been appended, the scraper accesses each of these links and scrapes the
webpages corresponding to these links for the starting XIs of both the home team and the away team
in these games. Once again, the combination of home team, away team, and season, is used as a key
of sorts to match these starting xis to the corresponding games

Also, it is important to note here that much of the code is contained within loops that
combined for loops and try + except statements. Here the intention is to make sure that 
the code is forced to run even if it doesn't work the first time (due to the unreliable 
nature of selenium and the website being accessed)'''

starting_xi = pd.DataFrame(columns = ['Season', 'Home Team', 'Away Team', 'Home Team XI', 'Away Team XI'])
links = []
season_list = []
whoscored = 'https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League'



driver = webdriver.Chrome(executable_path = C_DRIVER_PATH)

#scraping whoscored for the links
for season in full_seasons:
    
    driver.get(whoscored)
    driver.maximize_window()
    time.sleep(5)
    
    #closing ads
    try:
        close_ad_button = driver.find_element(By.CLASS_NAME, 'webpush-swal2-close')
        close_ad_button.click()
    except:
        pass
    
    #selecting the season
    dropdown = driver.find_element_by_id("seasons")
    dropdown.click()
    time.sleep(5)
    xpath = f".//*[contains(text(), '{season}')]"
    season_option = driver.find_element_by_xpath(xpath)
    season_option.click()
    
    #Note, the results for each season are grouped by year+month, so accessing a new page requires selecting the year and month
    
    #opening the menu that allows one to select the date
    for dummy in range(100):
        try:
            monthly_list = driver.find_element_by_id("link-fixtures")
            monthly_list.click()
            break
        except:
            print("can't find link button")
    time.sleep(2)
    match_counter = 0
    
    #finding the clickable elements corresponding to the month and year selection (so that they can later be looped through)
    for dummy in range(100):
        try:
            date_selector = driver.find_element(By.ID, "date-config-toggle-button")
            date_selector.click()
            big_box = driver.find_element(By.CSS_SELECTOR, ".datepicker.archive.monthly-selection")
            year_table = big_box.find_element(By.CLASS_NAME, "years")
            years = year_table.find_elements(By.CLASS_NAME, "selectable")
            break
        except:
            pass
    
    
    for year_num in range(len(years)):
        
        '''selecting the year (note: here years corresponds to the years 
        corresponding to the season being looped through, so since seasons go from 
        fall to summer the following year, there are always only two years) '''
        for dummy in range(100):
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                big_box = driver.find_element(By.CSS_SELECTOR, ".datepicker.archive.monthly-selection")
                year_table = big_box.find_element(By.CLASS_NAME, "years")
                years = year_table.find_elements(By.CLASS_NAME, "selectable")
                year = years[year_num]
                year.click()
                time.sleep(1.5)
                big_box = driver.find_element(By.CSS_SELECTOR, ".datepicker.archive.monthly-selection")
                
                #the month-selection elements need to be loaded for them to later be looped through
                month_table = big_box.find_element(By.CLASS_NAME, "months")
                months = month_table.find_elements(By.CLASS_NAME, "selectable")
                break
            except:
                #print("can't select year")
                pass
        
        
        for month_num in range(len(months)):
            #looping through the months in year 'year_num' corresponding to the season being looped through
            for dummy in range(100):
                try:
                    #selecting the month
                    time.sleep(1)
                    big_box = driver.find_element(By.CSS_SELECTOR, ".datepicker.archive.monthly-selection")
                    month_table = big_box.find_element(By.CLASS_NAME, "months")
                    months = month_table.find_elements(By.CLASS_NAME, "selectable")
                    month = months[month_num]
                    month.click()
                    (time.sleep(1.5))
                    break
                except:
                    #print("can't select month")
                    pass
            
            try:
                date_button = driver.find_element(By.ID, "date-controller")
                #print(date_button.text)
                pass
            except:
                pass
            
            #scrolling to the bottom to load all the fixtures from the month
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            #extracting all the rows from the table that stores the fixtures
            for i in range(20):
                try:
                    fixtures_table = driver.find_element(By.ID, "tournament-fixture")
                    matches = fixtures_table.find_elements_by_class_name("divtable-row")
                    break
                except:
                    pass
            
            '''removing all the rows that don't correspond to matches, and instead correspond to sub-headings
            These rows are easily identifiable because they have no links'''
            to_remove = []
            for row in matches:
                try:
                    check_for_link = row.find_element(By.TAG_NAME,'a')
                except:
                    to_remove.append(row)
            for elem in to_remove:
                matches.remove(elem)
            
            
            l = len(matches)
            for match_num in range(l):
                
                '''here I am reloading fixtures_table and re-removing the non-match rows
                to make sure that unexpected stale element errors don't occur'''
                
                fixtures_table = driver.find_element(By.ID, "tournament-fixture")
                matches = fixtures_table.find_elements_by_class_name("divtable-row")
    
                to_remove = []
                for row in matches:
                    try:
                        check_for_link = row.find_element(By.TAG_NAME,'a')
                    except:
                        to_remove.append(row)
                for elem in to_remove:
                    matches.remove(elem)
                
                #extracting the link to the match details
                header = driver.find_element_by_tag_name("h1")
                header.click()
                match = matches[match_num]
                results_box = match.find_element(By.CSS_SELECTOR, ".col12-lg-1.col12-m-1.col12-s-0.col12-xs-0.result.divtable-data")
                match_link = results_box.find_element(By.TAG_NAME, "a")
                match_link = match_link.get_attribute("href")
                links.append(match_link)
                season_list.append(season)

'''the second part of the scraping consists of opening all the links and scraping the pages
that they lead to for the starting xis of the teams '''

for data_num in range(len(links)):
    print(data_num)
    driver.get(links[data_num])
    season = season_list[data_num]
    home_players = []
    away_players = []
    
    #these variables are initialized for the purposes of the while statement below
    home_team = ""
    away_team = ""
    
    '''while scraping I sometimes encountered an error whereby which a team's name would be 
    scraped and returned as an empty string. This while statement forces the code to run until this
    isn't the case, thereby preventing this error '''
    
    while (len(home_team) * len(away_team) == 0) or (home_team[0] == " "):
        try:
            
            #navigating the page to find the starting xis
            banner = driver.find_element_by_id("match-header")
            action = ActionChains(driver)
            action.move_to_element(banner)
            
            team_names = banner.find_elements(By.CLASS_NAME, "team-link")
            home_team = name_corrector(team_names[0].text)
            away_team = name_corrector(team_names[1].text)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3.5);")

            pitch = driver.find_element(By.CLASS_NAME, "pitch")
            pitch_sides = pitch.find_elements(By.CLASS_NAME, "pitch-field")
            home_pitch = pitch_sides[0]
            away_pitch = pitch_sides[1]
            hplayers = home_pitch.find_elements(By.CLASS_NAME, "player-name")
            aplayers = away_pitch.find_elements(By.CLASS_NAME, "player-name")
            
            for i in hplayers:
                home_players.append(i.text)
            for i in aplayers:
                away_players.append(i.text)
            break
        except:
            #print("failed")
            pass
    length = starting_xi.shape[0]
    
    #adding a new row to the starting xi dataframe
    starting_xi.loc[length] = [season, home_team, away_team, home_players, away_players]
            
            
            
starting_xi.to_excel(starting_xi_data)
#print(starting_xi)
        
                                        
        
        
        
        
        
                    
        

        
        
                                      
        
        
        