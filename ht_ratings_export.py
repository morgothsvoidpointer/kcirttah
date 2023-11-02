# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:51:34 2023

@author: Tyufik
"""
from datetime import datetime
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# set options to be headless
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

import requests
from bs4 import BeautifulSoup as bs
#%%
def get_NT_match_IDs(NT_ID, seasons):
    list_of_match_ids = []

    for season in seasons:
        response = requests.get('https://www.hattrick.org/en/Club/Matches/Archive.aspx?season=' + str(season) + '&TeamID=' + str(NT_ID))
        soup = bs(response.content)
        match_links = soup.find_all('a', title="Lineup")

        for match_link in match_links:
            match_link = str(match_link)
            match_id = match_link[45:53]
            match_id = int(match_id)
            list_of_match_ids.append(match_id)

    return list_of_match_ids


nt_match_ids=get_NT_match_IDs(3001, [85, 84])

#%%
import math
def drop_ts(G4):
    ts_new=-0.0046*(G4-5)^2+(G4-5)*(0.0932+0.0278*math.tanh((G4-5-4.65)/0.2))
    return(ts_new)


#%%

def style_of_play_parser(sop):
    if 'Neutral' in sop:
        return 0
    elif 'Defensive' in sop:
        return  0-int(re.findall(r'\d+',sop)[0])
    elif 'Offensive' in sop or 'Attacking' in sop:
        return  int(re.findall(r'\d+',sop)[0])
            
def get_nt_match_ratings(nt_match_id,debug_on=0):

    driver.get(url='https://www.hattrick.org/en/Club/Matches/Match.aspx?matchID=' + str(nt_match_id) + '&SourceSystem=HTOIntegrated')
    time.sleep(5)
    table_head = driver.find_elements(By.TAG_NAME, 'th')
    cells = driver.find_elements(By.TAG_NAME, 'td')
    match_data={
        'Match Datetime': datetime.strptime(driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[2]/span[1]').text,'%d/%m/%Y %H.%M'),
        'Match Type': driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[1]').text
        }
    
    try:
        table_head[2].text
    except IndexError:
        print('something wrong with match import')
        print(table_head)
    
    print('processing '+table_head[2].text+' vs '+ table_head[4].text)
    
    #find 'average goals'
    cells_text=[cells[i].text for i in range(len(cells))]
    avggoal_index=cells_text.index('Average goals')
    print('average goals at '+str(avggoal_index))
    totalexp_index=cells_text.index('Total player experience')
    
    
    team_A = {
        'Team name': table_head[2].text,
        'Midfield': float(cells[3].text.replace(',','.')),
        'Right defence': float(cells[10].text.replace(',','.')),
        'Central defence':float(cells[17].text.replace(',','.')),
        'Left defence': float(cells[24].text.replace(',','.')),
        'Right attack': float(cells[31].text.replace(',','.')),
        'Central attack': float(cells[38].text.replace(',','.')),
        'Left attack': float(cells[45].text.replace(',','.')),
        'ISP defence': float(cells[52].text.replace(',','.')),
        'ISP attack': float(cells[59].text.replace(',','.')),
        'Tactic': cells[70].text,
        'Tactic skill': cells[76].text,
        'Total exp': float(cells[totalexp_index+3].text.replace(',','.')),
        'Style of play': style_of_play_parser(cells[79].text),
        'Average goals': float(cells[avggoal_index-1].text.replace(',','.'))
    }
    team_B = {
        'Team name': table_head[4].text,
        'Midfield': float(cells[6].text.replace(',','.')),
        'Right defence': float(cells[13].text.replace(',','.')),
        'Central defence':float(cells[20].text.replace(',','.')),
        'Left defence': float(cells[27].text.replace(',','.')),
        'Right attack': float(cells[34].text.replace(',','.')),
        'Central attack': float(cells[41].text.replace(',','.')),
        'Left attack': float(cells[48].text.replace(',','.')),
        'ISP defence': float(cells[55].text.replace(',','.')),
        'ISP attack': float(cells[62].text.replace(',','.')),
        'Tactic': cells[72].text,
        'Tactic skill': cells[78].text,
        'Total exp': float(cells[totalexp_index+6].text.replace(',','.')),
        'Style of play': style_of_play_parser(cells[81].text),
        'Average goals': float(cells[avggoal_index+1].text.replace(',','.'))
    }
    if debug_on:
        for i in range(len(cells)):
            if len(cells[i].text)>0:
                print(i)
                print(cells[i].text)
        for i in range(len(table_head)):
            if len(table_head[i].text)>0:
                print(i)
                print(table_head[i].text)
    
    
    return team_A, team_B, match_data
    
nt_match_id = 31515894

team_A, team_B, match_data = get_nt_match_ratings(nt_match_id)
print('match data = '+str(match_data))
print('Team A = ', team_A)
print('Team B = ', team_B)

#%%
team_a_list=[]
team_b_list=[]
match_list=[]
for ntmid in nt_match_ids:
    team_A, team_B,match_data = get_nt_match_ratings(ntmid)
    team_a_list.append(team_A)
    team_b_list.append(team_B)
    match_list.append(match_data)
    
#%%
import pandas as pd
home_ratings=pd.DataFrame(team_a_list)
away_ratings=pd.DataFrame(team_b_list)
oor_team=pd.unique(home_ratings['Team name'])[0]    


H='H'
A='A'
overall_ratings_=pd.concat([home_ratings,pd.Series([H]*len(team_a_list))\
                            ,away_ratings,pd.Series([A]*len(team_b_list))],axis=1)
overall_ratings_list=[]

team_names=overall_ratings_['Team name'].values
home_or_away=[]
for row in team_names:
    if oor_team==row[0]:
        home_or_away.append(0)
    elif oor_team==row[1]:
        home_or_away.append(1)
    else:
        print('something is wrong')


#correct tactic rating
for r in away_ratings.index:
    if away_ratings['Tactic'].loc[r]=='Normal':
        away_ratings['Tactic skill'].loc[r]=None
    elif away_ratings['Tactic'].loc[r]=='Counter-attacks' or \
        away_ratings['Tactic'].loc[r]=='Play creatively':
        ts=away_ratings['Tactic skill'].loc[r]
        if not isinstance(ts,str):
            continue
        if 'divine' in ts:
            divin=re.search(r'\d+', ts).group()
            
            away_ratings['Tactic skill'].loc[r]=20+int(divin)

        if ts=='utopian\nutopian':
            away_ratings['Tactic skill'].loc[r]=19
        if ts=='magical\nmagical':
            away_ratings['Tactic skill'].loc[r]=18
        if ts=='mythical\nmythical':
            away_ratings['Tactic skill'].loc[r]=17
        else:
            print('new rating')
            print(ts)
            break            
            
        
overall_ratings=[]
for r in overall_ratings_.index:
    row=overall_ratings_.loc[r]
    if home_or_away[r]==1:
        #swap the ratings of home and away side
        
        #print(row)
        l=int(len(row)/2)
        new_row=row[l:]._append(row[:l])
        overall_ratings.append(list(new_row))
    else:
        overall_ratings.append(list(row))
    #if r==0: break

overall_ratings_pd=pd.concat([pd.DataFrame(match_data),pd.DataFrame(overall_ratings)],axis=1)



