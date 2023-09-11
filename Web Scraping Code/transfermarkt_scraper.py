# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 23:32:49 2023

@author: veerg
"""

'''this code scrapes the transfermarkt website to create a json file that
has information on the transfer values of every player that played in the PL in the specificed
time period across all the seasons they were in the premier league. This is then
combined with the results of the starting xi scraper to work out the total transfer value
of the starting xis in each game, which is meant to act as an indicator of the reputation
and perceived quality of each teams starting xi'''

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
import pandas as pd
import numpy as np
import json


import copy
    
ok = False
scraped_data = pd.read_excel(PL_website_data)
scraped_data = scraped_data.drop(scraped_data.columns[0], axis = 1)
scraped_data['season'] = scraped_data['season'].apply(season_corrector)
scraped_data['Home Team'] = scraped_data['Home Team'].apply(name_corrector)
scraped_data['Away Team'] = scraped_data['Away Team'].apply(name_corrector)



transfermarkt = "https://www.transfermarkt.us"




#OPENING UP WEBSITE AND GETTING PAST TERMS AND CONDITIONS
driver = webdriver.Chrome(C_DRIVER_PATH)
driver.get(transfermarkt)
time.sleep(1.5)
driver.switch_to.frame("sp_message_iframe_852092")
accept = driver.find_element_by_xpath('//*[@id="notice"]/div[3]/div[3]/button')
accept.click()
driver.maximize_window()

team_list = scraped_data['Home Team'].drop_duplicates()
team_list = team_list.tolist()

transfer_values = {}
        

#print(team_list)

for team in team_list:
    
    #searching for and clicking on the team via transfermarkt's search function
    search_bar = driver.find_element_by_name('query')
    ok = False
    print('searching...')
    while ok == False:
        try:
            search_bar.send_keys(team)
            search_bar.send_keys(Keys.RETURN)
            ok = True
        except:
            pass
    print('searched')
    time.sleep(2.5)
    
    try: 
        ad_button = driver.find_element_by_tag_name("path")
        ad_button.click()
        print("ad clicked")
    except:
        pass
    
    time.sleep(1)
    results_tables = driver.find_elements_by_class_name("responsive-table")
    
    for table in results_tables:
        actions = ActionChains(driver)
        actions.move_to_element(table).perform()
        time.sleep(1)
        try:
            TMV = table.find_element_by_xpath(".//*[contains(text(), 'forum')]")
            correctTable = table
            break
            
        
        except:
            pass
            
            
    team_row = correctTable.find_element_by_class_name("odd")       
    team_link = team_row.find_element_by_class_name("hauptlink")
    ok = False
    while ok == False:
        try:
            team_link.click()
            ok = True
        except:
            pass
        
    time.sleep(1.5)
    
    #scraping transfer value data
    
    team_transfer_values = {}
    counter = 0
    for season in seasons:
        player_value_dict = {}
        time.sleep(1.5)
        try:
            ad = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "closeIconHit")))
            ad.click()
        except:
            pass
        
        #lower_part = driver.find_element(By.CLASS_NAME,  "large-4")
        element_to_move_to = driver.find_element(By.XPATH, '//*[@id="yw1_c1"]/a')
        while ok == False:
            try:
                action = ActionChains(driver)
                action.move_to_element_with_offset(element_to_move_to, 5, 5).perform()
                ok = True
            except:
                pass
        time.sleep(5)
        
  
        try: 
            ad_button = driver.find_element_by_tag_name("path")
            ad_button.click()
            #print("ad clicked")
        except:
            pass
        
        time.sleep(1.5)
        dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div[2]/div[1]/div[1]/div[1]/form/div/div/table/tbody/tr/td[2]/div/div/a/div/b'))
)
        ok = False
        while ok == False:
            try:
                dropdown.click()
                ok = True
            except:
                pass
        dropdown_results = driver.find_element_by_class_name("chzn-results")
        action = ActionChains(driver)
        table = driver.find_element_by_id('yw1')
        second_row = table.find_elements_by_class_name("even")
        action.move_to_element(second_row[1]).perform()
        search_bar = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[2]/div[1]/div[1]/div[1]/form/div/div/table/tbody/tr/td[2]/div/div/div/div/input')
        ok = False
        while ok == False:
            try:
                search_bar.send_keys(season)
                search_bar.send_keys(Keys.RETURN)
                ok = True
            except:
                pass
        show_button = driver.find_element(By.CLASS_NAME, "small")
        show_button.click()
        
        #scrolling down again once you've selected the season and the page has loaded
        
        try:
            ad = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "closeIconHit")))
            ad.click()
        except:
            pass
        
        #lower_part = driver.find_element(By.CLASS_NAME,  "large-4")
        element_to_move_to = driver.find_element(By.XPATH, '//*[@id="yw1_c1"]/a')
        action = ActionChains(driver)
        ok = False
        while ok == False:
            try:
                action.move_to_element_with_offset(element_to_move_to, 5, 5).perform()
                ok = True
            except:
                pass
        time.sleep(5)
        
        try: 
            ad_button = driver.find_element_by_tag_name("path")
            ad_button.click()
            #print("ad clicked")
        except:
            pass
        
        table = driver.find_element_by_id('yw1')
        second_row = table.find_elements_by_class_name("even")
        action.move_to_element(second_row[1]).perform()

        name_values = table.find_elements_by_class_name("hauptlink")
        transfer_vals = table.find_elements_by_css_selector(".rechts.hauptlink")
        t_values = []
        names = []
    
        for name_value_pair in name_values:
            if name_values.index(name_value_pair)%2 == 0:
                names.append(name_value_pair.text)
            else:
                t_values.append(transfer_vals_func(name_value_pair.text))
        #Creating player-value dictionary
        
        for index in range(len(t_values)):
            player_value_dict[names[index]] = t_values[index] 
            
            
        driver.execute_script("window.scrollTo(0, 0);")
        driver.execute_script("window.scrollTo(0, 0);")
        team_transfer_values[season] = player_value_dict
        print(team + " " + season)
            
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    #exitting the page, end of loop
    transfer_values[team] = team_transfer_values
    time.sleep(3)
    
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    search_bar = driver.find_element_by_name('query')
    ok = False
    while ok == False:
        try:
            search_bar.clear()
            ok = True
            break
        except:
            pass
    
    
    
    
    
    
    
    time.sleep(2)

print(transfer_values)

# Open a JSON file for writing
with open(transfer_value_data, 'w') as f:
    # Serialize the dictionary and write it to the file
    json.dump(transfer_values, f)



