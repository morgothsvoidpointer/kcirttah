# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:51:34 2023

@author: Tyufik
"""

import numpy as np
import pandas as pd

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

nt_id=3186
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


nt_match_ids=get_NT_match_IDs(nt_id, [85, 84])

#%%
import math
def drop_ts(G4):
    ts_new=-0.0046*(G4-5)^2+(G4-5)*(0.0932+0.0278*math.tanh((G4-5-4.65)/0.2))
    return(ts_new)

def ts_data_import(nt_id=3001):
    data=[]
    f=open(str(nt_id)+'_ts_data.txt',mode='r')
    while(1):
        L=f.readline()
        #print(L)
        if L=='EOF' or len(L)==0:
            break
        Llist=L.split()
        Date=datetime.strptime(Llist[0],'%m/%d/%Y')
        ts_found=0
        tc_found=0
        
        for l in Llist:
            if l.isdigit() and ts_found==0:
                ts_found=1
                ts=l
            elif l.isdigit() and tc_found==0:
                tc_found=1
                tc=l
            elif l.isdigit():
                print('what is this number '+l+'?')
        if ts_found and tc_found:
            data.append([Date,ts,tc])
        elif ts_found and not tc_found:
            data.append([Date,ts,None])
        elif not ts_found and not tc_found:
            data.append([Date,None,None])
    data=pd.DataFrame(data)
    data.columns=['datetime','team spirit','confidence']
    return data

ts_data=ts_data_import(nt_id=3001)

def attitude_guess(ts_data,match_datetimes):
    ts_locat=0
    team_spirits=[]
    team_spirits_next=[]
    match_attitudes=[]
    for match_datetime in match_datetimes.values:
        #find location in ts_list
        try:
            match_date=match_datetime.date()
        except AttributeError:
            md=pd.to_datetime(match_datetime)
            match_date=md.date()

        matched_date_rows=[]
        while 1:
            #find closest dates to match date
            
            ts_date=ts_data['datetime'][ts_locat].date()
            
            
            if match_date==ts_date:
                matched_date_rows.append(ts_locat)
                
            if ts_date<match_date:
                print('md')
                print(match_date)
                print('ts')
                print(ts_date)
                print(matched_date_rows)
                
                if len(matched_date_rows)==2:
                    ts=int(ts_data['team spirit'][matched_date_rows[1]])
                    ts_next=int(ts_data['team spirit'][matched_date_rows[0]])
                    team_spirits.append(ts)
                    team_spirits_next.append(ts_next)
                    if ts_next>ts and ts>4:
                        match_attitudes.append(4/3)#PIC with ts about composed
                    elif ts_next>1.2*ts and ts<5:
                        match_attitudes.append(4/3)#PIC with ts below calm 
                    elif ts_next<0.66*ts:
                        match_attitudes.append(1/2)#MOTS
                    else:
                        match_attitudes.append(1)
                        

                elif len(matched_date_rows)==1:
                    ts=int(ts_data['team spirit'][matched_date_rows[0]])
                    ts_next=int(ts_data['team spirit'][matched_date_rows[0]-1])
                    ts_prev=int(ts_data['team spirit'][matched_date_rows[0]+1])
                    if ts_next>ts and ts>4 or ts_next>1.2*ts and ts<5:
                        match_attitudes.append(4/3)
                        team_spirits.append(ts)
                        team_spirits_next.append(ts_next)
                        
                    elif ts>ts_prev and ts_prev>4 or ts>1.2*ts_prev and ts_prev<5:
                        match_attitudes.append(4/3)
                        team_spirits.append(ts_prev)
                        team_spirits_next.append(ts)
                        
                    elif ts_next<0.66*ts:
                        match_attitudes.append(1/2)
                        team_spirits.append(ts)
                        team_spirits_next.append(ts_next)
                        
                    elif 0.66*ts_prev>ts:
                        match_attitudes.append(1/2)
                        team_spirits.append(ts_prev)
                        team_spirits_next.append(ts)

                    else:
                        match_attitudes.append(1)
                        team_spirits.append(ts)
                        team_spirits_next.append(ts_next)                        
                elif len(matched_date_rows)==0:         
                    ts=int(ts_data['team spirit'][ts_locat])
                    ts_next=int(ts_data['team spirit'][ts_locat-1]) 
                    team_spirits.append(ts)
                    team_spirits_next.append(ts_next)
                    if ts_next>ts and ts>4:
                        match_attitudes.append(4/3)#PIC with ts about composed
                    elif ts_next>1.2*ts and ts<5:
                        match_attitudes.append(4/3)#PIC with ts below calm 
                    elif ts_next<0.66*ts:
                        match_attitudes.append(1/2)#MOTS
                    else:
                        match_attitudes.append(1)               
                    
                


                break
            ts_locat=ts_locat+1
    ts_array=pd.concat([pd.Series(match_datetimes),pd.Series(team_spirits),pd.Series(team_spirits_next),pd.Series(match_attitudes)],axis=1)
    return ts_array
            
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
    #print('average goals at '+str(avggoal_index))
    totalexp_index=cells_text.index('Total player experience')
    
    
    team_A = {
        'Team name': table_head[2].text,
        'Midfield': float(cells_text[3].replace(',','.')),
        'Right defence': float(cells_text[10].replace(',','.')),
        'Central defence':float(cells_text[17].replace(',','.')),
        'Left defence': float(cells_text[24].replace(',','.')),
        'Right attack': float(cells_text[31].replace(',','.')),
        'Central attack': float(cells_text[38].replace(',','.')),
        'Left attack': float(cells_text[45].replace(',','.')),
        'ISP defence': float(cells_text[52].replace(',','.')),
        'ISP attack': float(cells_text[59].replace(',','.')),
        'Tactic': cells_text[70],
        'Tactic skill': cells_text[76],
        'Total exp': float(cells_text[totalexp_index+3].replace(',','.')),
        'Style of play': style_of_play_parser(cells_text[79]),
        'Average goals': float(cells_text[avggoal_index-1].replace(',','.'))
    }
    team_B = {
        'Team name': table_head[4].text,
        'Midfield': float(cells_text[6].replace(',','.')),
        'Right defence': float(cells_text[13].replace(',','.')),
        'Central defence':float(cells_text[20].replace(',','.')),
        'Left defence': float(cells_text[27].replace(',','.')),
        'Right attack': float(cells_text[34].replace(',','.')),
        'Central attack': float(cells_text[41].replace(',','.')),
        'Left attack': float(cells_text[48].replace(',','.')),
        'ISP defence': float(cells_text[55].replace(',','.')),
        'ISP attack': float(cells_text[62].replace(',','.')),
        'Tactic': cells_text[72],
        'Tactic skill': cells_text[78],
        'Total exp': float(cells_text[totalexp_index+6].replace(',','.')),
        'Style of play': style_of_play_parser(cells_text[81]),
        'Average goals': float(cells_text[avggoal_index+1].replace(',','.'))
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

def add_(s):
    return s+'_'

overall_ratings_pd=pd.concat([pd.DataFrame(match_list),pd.DataFrame(overall_ratings)],axis=1)
overall_ratings_pd.columns=overall_ratings_pd.columns[:2]\
    .union(home_ratings.columns,sort=False).union(pd.Series(['HomeOrAway']),sort=False)\
    .union(pd.Series(home_ratings.columns).apply(add_),sort=False).union(pd.Series(['HomeOrAway_']),sort=False)
#import team spirits - currently manual

match_datetimes=pd.Series(overall_ratings_pd['Match Datetime'])

ts_array=attitude_guess(ts_data,match_datetimes)

#now scale according to team spirit...
ts_multipliers=[\
    [10,122,142,162],\
    [9,116,135,154,],\
    [8,	110,	128,	146],\
    [7,	104,	121,	138],\
    [6,	98,	114,	130],\
    [5,	92,	107,	122],\
    [4,	87,	100,	113],\
    [3,	81,	93,	105],\
    [2,	75,	86,	97],\
    [1,	63,	72,	81],\
    [0,10,20,30]]
import numpy as np
ts_multipliers=np.array(ts_multipliers)

scaled_midfields=[]
for i in overall_ratings_pd.index:
    ts=ts_array[0]
    scaling=ts
    scaled_midfields.append(overall_ratings_pd['Midfield'].loc[i]*scaling)

    
    
"""
Playing Normal&Away	100%
Playing CA	93%
Playing at home	119.892%
Playing derby(away team)	111.493% •
Playing PIC	83.945%
Playing MOTS	111.49%
"""

"""
Paradise on Earth!	122%	142%	162%
walking on clouds	116%	135%	154%
delirious	110%	128%	146%
satisfied	104%	121%	138%
content	98%	114%	130%
calm	92%	107%	122%
composed	87%	100%	113%
irritated	81%	93%	105%
furious	75%	86%	97%
murderous	63%	72%	81%
"""



