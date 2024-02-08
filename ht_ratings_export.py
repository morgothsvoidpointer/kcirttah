# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:51:34 2023

@author: Tyufik
"""
import os
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime,timedelta
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

from github_upload import github_upload

nt_id=3172
attitudes_override=1
match_venue_forthem='A'
import_from_remote=0






home_multiplier=1.19892
ca_multiplier=0.93
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

try:
    nt_match_ids=get_NT_match_IDs(nt_id, [86, 85, 84])
except:
    print('no connection to site')

#%% TS evolution
import math
def drop_ts(G4):
    ts_new=-0.0046*(G4-5)**2+(G4-5)*(0.0932+0.0278*math.tanh((G4-5-4.65)/0.2))
    return(G4-ts_new)

def rise_ts(TSold):
    deltaTS=5-TSold
    dTS=0.0038*deltaTS**4 - 0.0246*deltaTS**3+0.0628*deltaTS**2+0.0202*deltaTS
    return TSold+dTS

def nan_subtract(L1,L2):
    L=[]
    for i in range(len(L1)):
        if i<len(L2):
            try:
                a=L1[i]-L2[i]
            except TypeError:
                L.append(None)
            else:
                L.append(a)
    return L

season_start_date84=datetime(2023,3,6)
season_length=16*7
def ts_reset_times(season_start_date):
    cc_reset=season_start_date+timedelta(days=16)
    quali_reset=cc_reset+timedelta(days=53)
    wc_reset=cc_reset+timedelta(days=70)
    wcr2_reset=wc_reset+timedelta(days=63)
    wcr3_reset=wcr2_reset+timedelta(days=28)
    wcr4_reset=wcr3_reset+timedelta(days=14)
    return cc_reset,quali_reset,wc_reset,wcr2_reset,wcr3_reset,wcr4_reset


def ts_evolution(match_datetimes,match_type,ts_array,season_start_date,next_match_date=datetime.now(),debug_tsev=0):
#%% 
    match_attitude=ts_array[2]
    ts_integer=ts_array[0]
    
    if debug_tsev==1:
        match_datetimes=overall_ratings_pd['Match Datetime']
        match_type=overall_ratings_pd['Match Type']
        match_attitude=ts_array[2]
        season_start_date=season_start_date84
        next_match_date=datetime.now()
        
    

    match_dates=pd.Series([m.date() for m in match_datetimes])    

    cc_reset,quali_reset,wc_reset,wcr2_reset,wcr3_reset,wcr4_reset=ts_reset_times(season_start_date)
    current_ts=5
    curr_date=season_start_date
    try:
        curr_match_num=max(match_dates.index[match_dates>cc_reset])
    except TypeError:
        curr_match_num=max(match_dates.index[match_dates>cc_reset.date()])        
    ts_evol=[]
    dates_evol=[]
    ts_atmatch=[]
    ts_integer_match=[]
    #strip times from match dates:


    while 1:
        if curr_date<cc_reset:
            if curr_date in match_dates.values:
                ts_atmatch.append(None)
                ts_integer_match.append(None)
        
        
        
        if curr_date>=cc_reset:
            #daily update
           if current_ts>=5:
               current_ts=drop_ts(current_ts) 
           else: 
               current_ts=rise_ts(current_ts)
           #do resets
           if (curr_date-quali_reset).days%224==0 and 'Wildcard match 1 in World Cup' in match_type.values:
               current_ts=5
               #print('wc quali reset')
           elif (curr_date-wc_reset).days%224==0 and 'Match 1 in round I of World Cup' in match_type.values:
               current_ts=5
               #print('wc reset')
           elif (curr_date-wc_reset).days%224==0 and 'Round 1 in Nations Cup' in match_type.values:
               current_ts=5
               #print('wc reset')
           elif (curr_date-wcr2_reset).days%224==0 and 'Match 1 in round II of World Cup' in match_type.values:
               current_ts=current_ts-0.8*(current_ts-5)
               #print('wc rest round 2')
           elif (curr_date-wcr3_reset).days%224==0 and 'Match 1 in round III of World Cup' in match_type.values:
               current_ts=current_ts-0.6*(current_ts-5)
           elif (curr_date-wcr4_reset).days%224==0 and 'Match 1 in round IV of World Cup' in match_type.values:
               current_ts=current_ts-0.4*(current_ts-5)              
           elif (curr_date-cc_reset).days%224==0:
               current_ts=5

           #changes from matches:
           #print(curr_date)
           ts_evol.append(current_ts)     
           dates_evol.append(curr_date)
           
           if curr_date in match_dates.values:
               #print('match '+str(curr_date))
               mtype=match_type[curr_match_num]
               mdate=match_dates[curr_match_num]
               #print('match '+str(mdate))

               if mtype!='Friendly match':
                   att=match_attitude[curr_match_num]
                   
                   ts_atmatch.append(current_ts)#record TS BEFORE the match
                   ts_integer_match.append(ts_integer[curr_match_num])
                   current_ts=current_ts*att
               else:
                   ts_atmatch.append(None)
                   ts_integer_match.append(None)
               curr_match_num=curr_match_num-1#remember list is backwards
               
           else:
               #print('no match '+str(curr_date))
               pass
        curr_date=curr_date+timedelta(days=1)
      
        #if curr_date==season_start_date+timedelta(days=224):
            #break
        if curr_date>next_match_date.date():
            print('reached present day')
            break               
#%% 

    
    myFmt = mdates.DateFormatter('%d')
    
    
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(myFmt)
    plt.plot(dates_evol,ts_evol)
    plt.plot(ts_array['Match Datetime'],ts_array[0])
    for cc,mdt in enumerate(match_dates):
        if match_type[cc]!='Friendly match':
            plt.axvline(mdt)
    ax.axis(xmin=season_start_date,xmax=curr_date)
    fig.autofmt_xdate()
    plt.show()

    #plt.plot(dates_evol,ts_evol)
    #plt.plot(ts_array['Match Datetime'],ts_array[0])
    #plt.show()
    
    
    
    diff_ts=nan_subtract(ts_atmatch,ts_integer_match)
    plt.plot(diff_ts)
    plt.title('difference between propagated and actual team spirit at matches')
    plt.show()    
    
    ts_atmatch.reverse()
    ts_integer_match.reverse()

    return ts_evol,ts_atmatch,ts_integer_match
    

def ts_fit(match_dates,\
           match_type,\
           ts_array,\
           season_start_date,\
           debug_tsev=0):
    if debug_tsev==1:
        match_dates=overall_ratings_pd['Match Datetime']
        match_type=overall_ratings_pd['Match Type']
        match_attitude=ts_array[2]
        season_start_date=season_start_date84
    
    cc_reset,quali_reset,wc_reset,wcr2_reset,wcr3_reset,wcr4_reset=ts_reset_times(season_start_date)

    ts_array_dates=pd.Series([d.date() for d in ts_array['Match Datetime'] if d.date()>cc_reset.date()])

    
    ts_evol,ts_atmatch,ts_integer_match=ts_evolution(match_dates,match_type,ts_array,season_start_date,debug_tsev=0)
        
    ts_diff=np.array(ts_atmatch)-np.array(ts_integer_match)
    
    

    #find first discrepancy
    for j in range(len(ts_diff)):
        if ts_diff[j]>1:
            for possible_attitude in [1.2,1,4/3]:
                ts_array_trial=ts_array
                ts_array[2].loc[ts_array.shape[0]-j-1]=possible_attitude
                ts_evol,ts_atmatch,ts_integer_match=ts_evolution(match_dates,match_type,ts_array,season_start_date,debug_tsev=0)
                ts_diff=np.array(ts_atmatch)-np.array(ts_integer_match)
                print(ts_diff)
            break
            
    

#%% TS data
def ts_data_import(nt_id=3001):
    """
    This procedure reads and imports ts text files
    """
    data=[]
    f=open(str(nt_id)+'_ts_data.txt',mode='r')
    date_format_ts='month_first'
    while(1):
        L=f.readline()
        if L=='EOF' or len(L)==0:
            break
        
        numbers_inL=re.findall(r'\d+',L)
        
        Llist=L.split()
        try:
            Date=datetime.strptime(Llist[0],'%m/%d/%Y')
        except ValueError:
            Date=datetime.strptime(Llist[0],'%d/%m/%Y')
            date_format_ts='day_first'
            break
    
    while(1):
        L=f.readline()
        #print(L)
        if L=='EOF' or len(L)==0:
            break
        
        numbers_inL=re.findall(r'\d+',L)
        
        Llist=L.split()
        if date_format_ts=='month_first':
            Date=datetime.strptime(Llist[0],'%m/%d/%Y')
        elif date_format_ts=='day_first':
            Date=datetime.strptime(Llist[0],'%d/%m/%Y')            
        ts_found=0        
        if len(numbers_inL)==5:
            ts=numbers_inL[3]
            tc=numbers_inL[4]
            data.append([Date,ts,tc])
        elif len(numbers_inL)==3:
            data.append([Date,None,None])
        elif len(numbers_inL)==4:
            word=Llist[-1]
            if word in ['poor','decent','strong','wonderful','exaggerated']:
                tc=numbers_inL[3]
                data.append([Date,None,tc])
            else:
                ts=numbers_inL[3]
                data.append([Date,ts,None])
    data=pd.DataFrame(data)
    data.columns=['datetime','team spirit','confidence']
    #filling in missing values using the value just below
    last_ts=None
    last_tc=None
    for i in data.index[::-1]: 
        if data['team spirit'].loc[i] is not None:
            last_ts=data['team spirit'].loc[i]
        else:
            data['team spirit'].loc[i]=last_ts

        if data['confidence'].loc[i] is not None:
            last_tc=data['confidence'].loc[i]
        else:
            data['confidence'].loc[i]=last_tc
    
    return data


def attitude_guess(ts_data,match_datetimes,current_ts=5):
    ts_locat=0
    team_spirits=[]
    team_spirits_next=[]
    match_attitudes=[]
    
    ts_data_new=[]
    for i in ts_data.index:
        if ts_data['team spirit'].loc[i] is not None:
            ts_data_new.append(ts_data.loc[i])
    ts_data=pd.DataFrame(ts_data_new).reset_index(drop=True)
    
    ts_data.columns=['datetime','team spirit','confidence']
    
 
    
    for enm,match_datetime in enumerate(match_datetimes.values):

        #find location in ts_list
        try:
            match_date=match_datetime.date()
        except AttributeError:
            md=pd.to_datetime(match_datetime)
            match_date=md.date()
            
        matched_date_rows=[]
        while 1:
            #find closest dates to match date
            try:
                ts_date=ts_data['datetime'][ts_locat].date()
            except KeyError:
                print(ts_data)
                print(ts_locat)
                print(match_date)
                import bobex
            
            if match_date==ts_date:
                matched_date_rows.append(ts_locat)
                
            if ts_date<match_date:
                print(ts_date)
                print(match_date)
                break
            else: 
                ts_locat=ts_locat+1
        print(enm)   
        print('match date')
        print(match_date)
        print('team spirit record date')
        print(ts_date)
        print('number of matched rows:')
        print(matched_date_rows)
        
        
        if len(matched_date_rows)>2:
            ts=int(ts_data['team spirit'][matched_date_rows[-1]])
            #ts_next=int(ts_data['team spirit'][matched_date_rows[0]])
            ts_next=int(ts_data['team spirit'][matched_date_rows[1]])

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
        
        elif len(matched_date_rows)==2:
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
            ts_next=int(ts_data['team spirit'][max(matched_date_rows[0]-1,0)])
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
            if ts_locat>0:
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
            else:
                match_attitudes.append(np.NAN)
                team_spirits.append(ts)
                team_spirits_next.append(np.NAN)
                ts_next=np.NAN                       
        print('previous ts '+str(ts))
        print('next ts '+str(ts_next))
        print('match '+str(len(match_attitudes)))


        """
            if enm<len(match_datetimes)-1:
                match_datetime_prev=match_datetimes.values[enm+1]
                try:
                    match_date_prev=match_datetime_prev.date()
                except AttributeError:
                    md=pd.to_datetime(match_datetime_prev)
                    match_date_prev=md.date()
                    
                
                if ts_date<match_date_prev:
                    pass
                else:
                    ts_locat=ts_locat+1
            else:   
                ts_locat=ts_locat+1
       """
        
    ts_array=pd.concat([pd.Series(match_datetimes),pd.Series(team_spirits),pd.Series(team_spirits_next),pd.Series(match_attitudes)],axis=1)

    if np.isnan(ts_array[1].loc[0]):
        ts_array[1].loc[0]=current_ts
        prev_ts=ts_array[0].loc[0]
        if current_ts>prev_ts and current_ts>5:
            ts_array[2].loc[0]=4/3
        elif current_ts>1.2*prev_ts and current_ts<6:
            ts_array[2].loc[0]=4/3
        elif current_ts<0.66*prev_ts:
            ts_array[2].loc[0]=0.5
        else:
            ts_array[2].loc[0]=1
    return ts_array
            
#%%

def style_of_play_parser(sop):
    if 'Neutral' in sop:
        return 0
    elif 'Defensive' in sop:
        return  0-int(re.findall(r'\d+',sop)[0])
    elif 'Offensive' in sop or 'Attacking' in sop:
        return  int(re.findall(r'\d+',sop)[0])

def array_clean(ratings_array):
    C1=ratings_array['Tactic'].tolist()
    C2=ratings_array['Tactic skill'].tolist()
    for c,i in enumerate(C1):

        if i=='Normal':
            C1[c]='(no tactic)'
            C2[c]=0
        else:
            if not isinstance(C2[c],str):
                continue
            if C2[c]=='utopian\nutopian':
                C2[c]=19
            elif C2[c]=='magical\nmagical':
                C2[c]=18
            elif C2[c]=='mythical\nmythical':
                C2[c]=17
            elif C2[c]=='extra-terrestrial\nextra-terrestrial':
                C2[c]=16
            elif C2[c]=='titanic\ntitanic':
                C2[c]=15
            elif C2[c]=='supernatural\nsupernatural':
                C2[c]=14
            elif C2[c]=='world class\nworld class':
                C2[c]=13
            elif C2[c]=='magnificent\nmagnificent':
                C2[c]=12                
            elif C2[c]=='brilliant\nbrilliant':
                C2[c]=11
            elif C2[c]=='outstanding\noutstanding':
                C2[c]=10             
            elif C2[c]=='formidable\nformidable':
                C2[c]=9                
            elif C2[c]=='excellent\nexcellent':
                C2[c]=8
            elif C2[c]=='solid\nsolid':
                C2[c]=7
            elif 'divine' in C2[c]:
                divin=re.search(r'\d+', C2[c]+'0').group()
                
                C2[c]=20+int(divin)
    for c,i in enumerate(C2):
        C2[c]=int(C2[c])
    ratings_array['Tactic']=C1
    ratings_array['Tactic skill']=C2
    
    
    C3=ratings_array['Tactic_'].tolist()
    C4=ratings_array['Tactic skill_'].tolist()
    for c,i in enumerate(C3):
        if i=='Normal':
            C3[c]='(no tactic)'
            C4[c]=0
        else:
            if not isinstance(C4[c],str):
                continue
            if C4[c]=='utopian\nutopian':
                C4[c]=19
            elif C4[c]=='magical\nmagical':
                C4[c]=18
            elif C4[c]=='mythical\nmythical':
                C4[c]=17
            elif C4[c]=='extra-terrestrial\nextra-terrestrial':
                C4[c]=16
            elif C4[c]=='titanic\ntitanic':
                C4[c]=15
            elif C4[c]=='supernatural\nsupernatural':
                C4[c]=14
            elif C4[c]=='world class\nworld class':
                C4[c]=13
            elif C4[c]=='magnificent\nmagnificent':
                C4[c]=12                
            elif C4[c]=='brilliant\nbrilliant':
                C4[c]=11
            elif C4[c]=='outstanding\noutstanding':
                C4[c]=10
            elif C4[c]=='formidable\nformidable':
                C4[c]=9
            elif C4[c]=='excellent\nexcellent':
                C4[c]=8
            elif C4[c]=='solid\nsolid':
                C4[c]=7
            elif 'divine' in C4[c]:
                divin=re.search(r'\d+', C4[c]+'0').group()
                
                C4[c]=20+int(divin)
    for c,i in enumerate(C4):
        C4[c]=int(C4[c])
    ratings_array['Tactic_']=C3
    ratings_array['Tactic skill_']=C4
    return ratings_array



def match_type_abbrev(mt):
    if ' I ' in mt:
        return 'WC1'
    if ' II ' in mt:
        return 'WC2'
    if ' III ' in mt:
        return 'WC3'
    if ' IV ' in mt:
        return 'WC4'
    if ' V ' in mt:
        return 'WC5'
    if 'Round' in mt and 'World' not in mt:
        return 'CC'
    if 'Quarterfinals' in mt and 'World' in mt:
        return 'WCQF'
    if 'Quarterfinals' in mt and 'World' not in mt:
        return 'CCQF'    
    if 'Semi-finals' in mt and 'World' in mt:
        return 'WCSF'
    if 'Semi-finals' in mt and 'World' not in mt:
        return 'CCSF'
    if ' Final ' in mt and 'World' in mt:
        return 'WCF'
    if ' Final ' in mt and 'World' not in mt:
        return 'CCF'  
    
    if 'Wildcard' in mt:
        return 'Q'
    
    if 'Friendly' in mt:
        return 'F'
    


            
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
    if 'Average goals' not in cells_text:
        print('possible WO, skipping')
        return None,None,None
    avggoal_index=cells_text.index('Average goals')
    #print('average goals at '+str(avggoal_index))
    totalexp_index=cells_text.index('Total player experience')
    styleofplay_index=cells_text.index('Style of play')
    tacticskill_index=cells_text.index('Tactic skill')
    
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
        'Tactic skill': cells_text[tacticskill_index+3],
        'Total exp': float(cells_text[totalexp_index+3].replace(',','.')),
        'Style of play': style_of_play_parser(cells_text[styleofplay_index+2]),
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
        'Tactic skill': cells_text[tacticskill_index+5],
        'Total exp': float(cells_text[totalexp_index+6].replace(',','.')),
        'Style of play': style_of_play_parser(cells_text[styleofplay_index+4]),
        'Average goals': float(cells_text[avggoal_index+1].replace(',','.'))
    }
    
    
    spans = driver.find_elements(By.TAG_NAME, 'span')
    match_text = ''
    for i in range(70, 120):
        match_text += (spans[i].text)
    
    formations_text = re.findall("[2-5]-[2-5]-[0-3]", match_text)
    home_team_formation = formations_text[0]
    away_team_formation = formations_text[1]
    
    print(str(table_head[2].text)+' formation is '+str(home_team_formation))
    print(str(table_head[4].text)+' formation is '+str(away_team_formation))    

    number_of_home_defenders = int(home_team_formation[0])
    number_of_away_defenders = int(away_team_formation[0])

    number_of_home_mids=int(home_team_formation[2])
    number_of_away_mids=int(away_team_formation[2])    

    number_of_home_forwards=int(home_team_formation[4])
    number_of_away_forwards=int(away_team_formation[4])
    
    team_A['Defender_number']=number_of_home_defenders
    team_B['Defender_number']=number_of_away_defenders
    team_A['Mid_number']=number_of_home_mids
    team_B['Mid_number']=number_of_away_mids
    team_A['Forward_number']=number_of_home_forwards
    team_B['Forward_number']=number_of_away_forwards
    
    
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
    


#%%

"""
nt_match_id = 31515894

team_A, team_B, match_data = get_nt_match_ratings(nt_match_id)
print('match data = '+str(match_data))
print('Team A = ', team_A)
print('Team B = ',  team_B)
"""

if import_from_remote==True:
    team_a_list=[]
    team_b_list=[]
    match_list=[]
    for ntmid in nt_match_ids:
        team_A, team_B,match_data = get_nt_match_ratings(ntmid)
        if team_A is not None:
            team_a_list.append(team_A)
            team_b_list.append(team_B)
            match_list.append(match_data)
        
    
    
    
    
    home_ratings=pd.DataFrame([a for a in team_a_list if a is not None])
    away_ratings=pd.DataFrame([b for b in team_b_list if b is not None])
    matches_pd=pd.DataFrame([m for m in match_list if m is not None])
    home_ratings.to_csv('home_ratings_backup.csv',index=False)
    away_ratings.to_csv('away_ratings_backup.csv',index=False)
    matches_pd.to_csv('matches_data_backup.csv',index=False)
else:
    home_ratings=pd.read_csv('home_ratings_backup.csv',index_col=None)
    away_ratings=pd.read_csv('away_ratings_backup.csv',index_col=None)
    matches_pd=pd.read_csv('matches_data_backup.csv',index_col=None)
    matches_pd['Match Datetime']=[datetime.strptime(d,'%Y-%m-%d %H:%M:%S') for d in matches_pd['Match Datetime']]
    
#%% FORM AND SAVE PANDAS DF, WITH COUNTRY OF INTEREST ON THE LEFT

oor_team=home_ratings['Team name'].mode()[0]


H='H'
A='A'
overall_ratings_=pd.concat([home_ratings,pd.Series([H]*home_ratings.shape[0])\
                            ,away_ratings,pd.Series([A]*away_ratings.shape[0])],axis=1)
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

overall_ratings_pd=pd.concat([matches_pd,pd.DataFrame(overall_ratings)],axis=1)
overall_ratings_pd.columns=overall_ratings_pd.columns[:2]\
    .union(home_ratings.columns,sort=False).union(pd.Series(['HomeOrAway']),sort=False)\
    .union(pd.Series(home_ratings.columns).apply(add_),sort=False).union(pd.Series(['HomeOrAway_']),sort=False)

#add abbreviations:
opponents_short=[]
type_short=[]
match_date=[]
formation=[]
formation_=[]
tactic_short=[]
tactics_short_dict={'(no tactic)':'N','Normal':'N','Counter-attacks':'CA','Pressing':'Pr',\
                    'Play creatively':'PC','Attack in the Middle':'AIM',\
                        'Attack on wings':'AOW','Long shots':'LS'}

for i in overall_ratings_pd.index:
    row=overall_ratings_pd.loc[i]
    opponents_short.append(row['Team name_'][:3])
    type_short.append(match_type_abbrev(row['Match Type']))
    match_date.append(row['Match Datetime'].date())
    formation.append('-'.join(map(str,row[['Defender_number', 'Mid_number', 'Forward_number']].tolist())))
    formation_.append('-'.join(map(str,row[['Defender_number_', 'Mid_number_', 'Forward_number_']].tolist())))
    tactic_short.append(tactics_short_dict[row['Tactic']])
    
overall_ratings_pd['MT']=type_short
overall_ratings_pd['Opponent']=opponents_short
overall_ratings_pd['Match Date']=match_date
overall_ratings_pd['Formation']=formation
overall_ratings_pd['Formation_']=formation_

overall_ratings_pd['Tactic short']=tactic_short
#CORRECTIONS OF MF RATING

#correct tactic ratings and name to fit convention
overall_ratings_pd=array_clean(overall_ratings_pd)

#correct for neutral venues

for i in range(overall_ratings_pd.shape[0]):
    matchtype=overall_ratings_pd['Match Type'].loc[i]
    if 'III' in matchtype or 'IV' in matchtype or ' V ' in matchtype or 'final' in matchtype:
        overall_ratings_pd['HomeOrAway'].iloc[i]='N'

#import team spirits - currently manual


ts_data=ts_data_import(nt_id)

overall_ratings_pd.to_csv(str(nt_id)+'_ratings_data.csv')

match_datetimes=pd.Series(overall_ratings_pd['Match Datetime'])

ts_array=attitude_guess(ts_data,match_datetimes)


#now scale by home or away

home_away_dict={}
home_away_dict['A']=1
home_away_dict['H']=home_multiplier
home_away_dict['N']=1
def home_away_scaling(HAN):
    return home_away_dict[HAN]

han_scalings=overall_ratings_pd['HomeOrAway'].apply(home_away_scaling)
scaled_midfields=overall_ratings_pd['Midfield']/han_scalings


if match_venue_forthem=='H':
    scaled_midfields=scaled_midfields*home_multiplier


#now scale according to team spirit...
def mf_at_ts(TS,mf_current,TS_current=5):
    """
    This function takes a TS value TS_current, takes a mf rating at TS_current and returns
    what that rating would be at TS
    """    
    #MF TS ( act) MF (TS = 9.5) = A+ B⋅TS +C ⋅TS2 + D⋅TS3 + E ⋅TS4 + F ⋅TS5 +G ⋅TS6
    A=0.29533
    B=0.12974 
    C=-6.9158e-3 
    D=-6.3908e-4 
    E=1.4072e-4 
    F=-6.433e-6 
    G=-3.7109e-9
    
    def polynom(TS):
        poly=A+B*TS+C*TS**2+D*TS**3+E*TS**4+F*TS**5+G*TS**6
        return poly
    
    
    mf95=mf_current/polynom(TS_current)
    mf=mf95*polynom(TS)

    return mf

def mf_at_ts_curr(mf):
    return mf_at_ts(curr_ts,mf,5)

    
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
    [0,50,60,70]]


    
ts_multipliers=pd.DataFrame(ts_multipliers)
ts_multipliers.index=ts_multipliers[0]
ts_multipliers.columns=[0,4/3,1,1/2]
ts=ts_array[0]
attitudes=ts_array[2].copy()

#At this point, everything is scaled to home/away PIN at TS 5, using rough TS
if attitudes_override:
    pass
    

    #to enter attitudes manually
    if nt_id==3156:
        #attitudes.loc[attitudes.shape[0]-6]=4/3
        #attitudes.loc[attitudes.shape[0]-8]=4/3
        #attitudes.loc[attitudes.shape[0]-9]=4/3
        attitudes.loc[attitudes.shape[0]-11]=4/3
        attitudes.loc[attitudes.shape[0]-15]=1/2
        attitudes.loc[attitudes.shape[0]-13]=4/3
        attitudes.loc[attitudes.shape[0]-23]=1
        attitudes.loc[attitudes.shape[0]-12]=0.5
    if nt_id==3116:
        attitudes.loc[attitudes.shape[0]-6]=1
        attitudes.loc[attitudes.shape[0]-9]=4/3
        attitudes.loc[attitudes.shape[0]-20]=4/3
        attitudes.loc[attitudes.shape[0]-21]=4/3
        attitudes.loc[attitudes.shape[0]-34]=4/3    
        
    if nt_id==3186:
        attitudes.loc[attitudes.shape[0]-5]=4/3
        attitudes.loc[attitudes.shape[0]-10]=4/3
        attitudes.loc[attitudes.shape[0]-12]=1/2
        attitudes.loc[attitudes.shape[0]-13]=1/2   
        attitudes.loc[attitudes.shape[0]-21]=4/3   
    if nt_id==3019:
        attitudes.loc[attitudes.shape[0]-5]=4/3
        attitudes.loc[attitudes.shape[0]-7]=4/3
        attitudes.loc[attitudes.shape[0]-25]=1
        
    if nt_id==3023:
        attitudes.loc[attitudes.shape[0]-8]=4/3
        attitudes.loc[attitudes.shape[0]-7]=4/3
        attitudes.loc[attitudes.shape[0]-5]=4/3
        attitudes.loc[attitudes.shape[0]-29]=4/3
    if nt_id==3222:
        attitudes.loc[attitudes.shape[0]-48]=1        
        attitudes.loc[attitudes.shape[0]-47]=4/3
        attitudes.loc[attitudes.shape[0]-45]=4/3
        attitudes.loc[attitudes.shape[0]-5]=4/3
        attitudes.loc[attitudes.shape[0]-17]=4/3
        
    if nt_id==3084:
        attitudes.loc[attitudes.shape[0]-12]=1/2        
        attitudes.loc[attitudes.shape[0]-15]=1/2            
        attitudes.loc[attitudes.shape[0]-18]=4/3
          
ts_array[2]=attitudes.round(decimals=1)
ts_evol,ts_atmatch,ts_integer=ts_evolution(match_datetimes=overall_ratings_pd['Match Datetime'],\
                     match_type=overall_ratings_pd['Match Type'],\
                     ts_array=ts_array,\
                     season_start_date=season_start_date84.date())
ts_array[3]=ts_atmatch
ts_array[4]=scaled_midfields
ts_array[5]=overall_ratings_pd['Midfield']
ts_array['Match Datetime']=overall_ratings_pd['Match Date']
ts_array[6]=None
ts_array[7]=overall_ratings_pd['MT']
ts_array[8]=overall_ratings_pd['HomeOrAway']
ts_array[9]=overall_ratings_pd['Formation']
ts_array[10]=overall_ratings_pd['Tactic short']
pd.set_option('display.max_columns', 15)



curr_ts=ts_evol[-1]

#cycle through midfields. We need to still establish the order.....
S=[]
for i in range(overall_ratings_pd.shape[0]):
    midr=overall_ratings_pd.iloc[i]['Midfield']
    ts_best=ts_atmatch[i]
    if ts_best is None:
        S.append(None)
        continue
    loc=overall_ratings_pd.iloc[i]['HomeOrAway']
    att=attitudes[i]
    
    midr_withts=mf_at_ts(curr_ts,midr,ts_best)
    if loc=='H' and match_venue_forthem in ['A','N']:
        midr_with_han=midr_withts/home_multiplier
    elif loc in ['A','N'] and match_venue_forthem=='H':
        midr_with_han=midr_withts*home_multiplier   
    else:
        midr_with_han=midr_withts
    if att<0.75:
        midr_with_attitude=midr_with_han/1.13
    elif att>1.2:
        midr_with_attitude=midr_with_han/0.87
    else: 
        midr_with_attitude=midr_with_han
    S.append(midr_with_attitude)
    #break


overall_ratings_pd['scaled_midfield']=S     
ts_array[6]=S

team_spirit_array=ts_array.copy()
team_spirit_array.columns=['Match Datetime','ts before','ts after',\
                  'attitude','ts evol','scaled mid','mid','away scaled mid',\
                      'location','match type','formation','tactic']
print(team_spirit_array)

if 'scaled midfield' not in overall_ratings_pd.columns:
    overall_ratings_pd.insert(3,'scaled midfield',S)
else:
    overall_ratings_pd['scaled midfield']=S   


overall_ratings_pd.to_csv(str(nt_id)+'_ratings_data.csv')


github_upload(str(nt_id)+'_ratings_data.csv')

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

#%% PREDICTOR




