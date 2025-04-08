# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 16:51:34 2023

@author: Tyufik
"""
import os
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
import math
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime,timedelta
import re
import time
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

desired_capabilities=DesiredCapabilities.CHROME.copy()
desired_capabilities['acceptInsecureCerts']=True

# set options to be headless
options = webdriver.ChromeOptions( )
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.set_capability('acceptInsecureCerts',True)



import requests  
from bs4 import BeautifulSoup as bs
"""

from github_upload import github_upload
from ehffutbol import ehffutbol_ts_tc,raw_text_output_process
from hatrick_api import get_match_data_chpp,get_match_list

nt_id=3001
match_venue_forthem='H'
import_from_remote=1
attitudes_override=1
import_from_remote_ts=1

"""
if import_from_remote or import_from_remote_ts:
    driver = webdriver.Chrome(options=options)
"""

home_multiplier=1.19892
derby_away_multiplier=1.11
ca_multiplier=0.93

season_start_date84=datetime(2023,3,6)
season_length=16*7

player_drop_events={}
if nt_id==3120:
    player_drop_events[datetime.strptime("2024-06-13","%Y-%m-%d").date()]=-1.08
if nt_id==3307:
    player_drop_events[datetime.strptime("2024-10-01","%Y-%m-%d").date()]=-4   
if nt_id==3022:
    player_drop_events[datetime.strptime("2024-10-07","%Y-%m-%d").date()]=-1.75   
if nt_id==3102:
    pass
    #player_drop_events[datetime.strptime("2024-06-13","%Y-%m-%d").date()]=-2.5   
    #player_drop_events[datetime.strptime("2024-08-23","%Y-%m-%d").date()]=-1.5   
if nt_id==3249:
    player_drop_events[datetime.strptime("2023-08-18","%Y-%m-%d").date()]=-5   
    player_drop_events[datetime.strptime("2023-10-05","%Y-%m-%d").date()]=-3   
    


#%%
"""
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
"""

#%% TS evolution

def drop_ts(TSold):
    dTS=(TSold-5)*(0.0932+0.0278*math.tanh((TSold-9.65)/0.2))-0.0046*(TSold-5)**2
    return(TSold-dTS)

#=-0,0046*(A2-5)^2+(A2-5)*(0,0932+0,0278*TANH((A2-5-4,65)/0,2)) 

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


def ts_reset_times(season_start_date):
    cc_reset=season_start_date+timedelta(days=16)
    quali_reset=cc_reset+timedelta(days=60)
    wc_reset=cc_reset+timedelta(days=70)
    wcr2_reset=wc_reset+timedelta(days=63)
    wcr3_reset=wcr2_reset+timedelta(days=28)
    wcr4_reset=wcr3_reset+timedelta(days=14)
    return cc_reset,quali_reset,wc_reset,wcr2_reset,wcr3_reset,wcr4_reset


def ts_evolution(match_datetimes,match_type,\
                 campaign_season_start,\
                 ts_array,season_start_date,\
                 player_drop_events={},\
                 next_match_date=datetime.now(),debug_tsev=0):
#%% 
    match_attitude=ts_array['att']
    ts_integer=ts_array['ts0']
    
    if debug_tsev==1:
        match_datetimes=overall_ratings_pd['Match Datetime']
        match_type=overall_ratings_pd['Match Type']
        campaign_season_start=overall_ratings_pd['campaign']
        match_attitude=ts_array['att']
        season_start_date=season_start_date84.date()
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
    
    current_campaign=campaign_season_start.values[-1]


    while 1:
        match_types_season=match_type[campaign_season_start==current_campaign]#isolate matches for current campaign only
        
        if curr_date<cc_reset:
            if curr_date in match_dates.values:
                ts_atmatch.append(None)
                ts_integer_match.append(None)
        
        
        
        if curr_date>=cc_reset:
            #changes from matches:
            #print(curr_date)
           #ts_evol.append(current_ts)
            #dates_evol.append(curr_date)
            
            #daily update
            
           #print('ts before update '+str(current_ts))
           if current_ts>=5:
               current_ts=drop_ts(current_ts)

           else: 
               current_ts=rise_ts(current_ts)
           #print('ts after update '+str(current_ts))
           #do resets
           if (curr_date-quali_reset).days%224==0 and 'W' in match_types_season.values:
               current_ts=5#wildcard

           elif (curr_date-wc_reset).days%224==0 and 'WC1' in match_types_season.values:
               current_ts=5
               print('wc quali reset at '+str(curr_date))
               #print('wc reset')
           elif (curr_date-wc_reset).days%224==0 and 'NC' in match_types_season.values:
               current_ts=5
               #print('wc reset')
           elif (curr_date-wc_reset).days%224==0 and (datetime.now().date()-curr_date).days<7:
               current_ts=5
           
            
           elif (curr_date-wcr2_reset).days%224==0 and 'WC2' in match_types_season.values:
               current_ts=current_ts-0.8*(current_ts-5)
               #print('wc rest round 2')
           
            
           elif (curr_date-wcr3_reset).days%224==0 and 'WC3' in match_types_season.values:
               current_ts=current_ts-0.6*(current_ts-5)
               
               
           elif (curr_date-wcr4_reset).days%224==0 and 'WC4' in match_types_season.values:
               current_ts=current_ts-0.4*(current_ts-5)
           elif (curr_date-wcr4_reset).days%224==0 and (datetime.now().date()-curr_date).days<7:
               current_ts=current_ts-0.4*(current_ts-5)   
           elif (curr_date-cc_reset).days%224==0:
               
               print('cc reset '+str(curr_date))
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

               if mtype!='F':
                   att=match_attitude[curr_match_num]
                   
                   ts_atmatch.append(current_ts)#record TS BEFORE the match
                   ts_integer_match.append(ts_integer[curr_match_num])
                   #print('ts before match '+str(current_ts))
                   if att==1.30:
                       att=4/3
                   current_ts=current_ts*att
                   #print('ts after match '+str(current_ts))
               else:
                   ts_atmatch.append(None)
                   ts_integer_match.append(None)
               
               curr_match_num=curr_match_num-1#remember list is backwards
               if curr_match_num>-1:
                   
                   current_campaign=campaign_season_start[curr_match_num]#change the campaign number for next iteration
           else:
               #print('no match '+str(curr_date))
               pass
           #player drop events
           if curr_date in player_drop_events.keys():
               current_ts=current_ts+player_drop_events[curr_date]
        curr_date=curr_date+timedelta(days=1)
        
      
        #if curr_date==season_start_date+timedelta(days=224):
            #break
        if curr_date>next_match_date.date():
            print('reached present day '+str(curr_date))
            break               
#%% 

    
    myFmt = mdates.DateFormatter('%d')
    
    
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(myFmt)
    plt.plot(dates_evol,ts_evol)
    plt.plot(ts_array['Match Datetime'],ts_array['ts0'])
    for cc,mdt in enumerate(match_dates):
        if match_type[cc]!='F':
            plt.axvline(mdt)
    ax.axis(xmin=season_start_date,xmax=curr_date)
    fig.autofmt_xdate()
    plt.show()

    #plt.plot(dates_evol,ts_evol)
    #plt.plot(ts_array['Match Datetime'],ts_array[0])
    #plt.show()
    
    
    
    diff_ts=nan_subtract(ts_atmatch,ts_integer_match)
    diff_ts.reverse()
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
        match_attitude=ts_array['att']
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
                ts_array['att'].loc[ts_array.shape[0]-j-1]=possible_attitude
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

def attitude_guess_ehff(ts_data,match_datetimes,player_drop_events={},current_ts=5):
    
    
    
    ts_data=ts_data.reset_index(drop=True)

    match_datetimes.sort_values(inplace=True,ignore_index=True)
    ts_data.sort_values(by='datetime',inplace=True)
    ts_data.to_csv('wtf2.csv')
    match_datetimes=pd.Series(match_datetimes.values)
    
    #cycle through the ts values and find 'windows' corresponding to matches
    match_dates=[match_datetimes[i].date() for i in range(len(match_datetimes))]
    ts_before_match=[]
    ts_at_match=[]
    ts_after_match=[]
    ts_before_match_local=[]
    ts_after_match_local=[]
    curr_match=0
    for i,ts_row in enumerate(ts_data.values):
        ts_date=ts_row[0].date()
        if ts_date in match_dates:
            print(ts_date)
            ts_at_match.append(ts_row)
            ts_before_match.append(ts_before_match_local)
            if curr_match>0:
                ts_after_match.append(ts_after_match_local)
            ts_before_match_local=[]
            ts_after_match_local=[]
            curr_match=curr_match+1            
        else:
            ts_before_match_local.append(ts_row)
            ts_after_match_local.append(ts_row)
    
        if i==len(ts_data.values)-1:
            ts_after_match.append(ts_after_match_local)
            
    #Now cycle through matches and examine team spirits either side
    match_attitudes=[]
    team_spirits=[]
    team_spirits_next=[]
    team_spirits_next2=[]
    team_spirits_next3=[]
    for i in range(len(match_dates)):
        print(i)
        print(match_dates[i])
        print(ts_at_match[i])
        #print(ts_at_match)
        ts_onday=ts_at_match[i][1]
        team_spirits.append(ts_onday)
        if len(ts_after_match[i])>0:
            ts_nextday=ts_after_match[i][0][1]
            team_spirits_next.append(ts_nextday)
        else:
            print('cannot evaluate attitude, match too recent')
            attitude=0
            match_attitudes.append(attitude)
            team_spirits_next.append(-1)
            team_spirits_next2.append(-1)
            team_spirits_next3.append(-1)
            continue
        if len(ts_after_match[i])>1:
            team_spirits_next2.append(ts_after_match[i][1][1])
            ts_day_after=ts_after_match[i][1][1]            
        else:
            team_spirits_next2.append(-1)
        if len(ts_after_match[i])>2:
            team_spirits_next3.append(ts_after_match[i][2][1])
        else:
            team_spirits_next3.append(-1)
        if ts_onday>4:
            if ts_nextday==10 and ts_day_after==10:
                attitude=4/3
            elif ts_nextday>ts_onday:
                attitude=4/3
            elif ts_nextday==ts_onday and ts_day_after>ts_onday:
                attitude=4/3
            elif ts_nextday<0.7*ts_onday:
                attitude=1/2
            else:
                attitude=1
                for j in range(1,len(ts_after_match[i])):
                    if ts_after_match[i][j][1]>ts_after_match[i][j-1][1] and ts_after_match[i][j][1]>4:
                        attitude=4/3
                        break
        else:
            if ts_nextday>1.2*ts_onday:
                attitude=4/3
            elif ts_nextday==ts_onday and ts_day_after>1.2*ts_nextday:
                attitude=4/3
            elif ts_nextday<0.7*ts_onday:
                attitude=1/2
            else: 
                attitude=1
        match_attitudes.append(attitude)
    ts_array=pd.concat([pd.Series(match_datetimes),\
                        pd.Series(team_spirits),pd.Series(team_spirits_next),\
                        pd.Series(team_spirits_next2),pd.Series(team_spirits_next3),\
                        pd.Series(match_attitudes)],axis=1)
        
    ts_array.columns=['Match Datetime','ts0','ts1','ts2','ts3','att']    
    ts_array.sort_values(by='Match Datetime',ascending=False,inplace=True,ignore_index=True)
#%%
    return ts_array

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
            except AttributeError:
                ts_date=ts_data['datetime'][ts_locat]
            
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
                team_spirits.append(ts)
                team_spirits_next.append(ts_next)
                
            elif ts_next<0.66*ts:
                match_attitudes.append(1/2)
                team_spirits.append(ts)
                team_spirits_next.append(ts_next)
                
            elif 0.66*ts_prev>ts:
                match_attitudes.append(1/2)
                team_spirits.append(ts)
                team_spirits_next.append(ts_next)

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

    if np.isnan(ts_array['ts1'].loc[0]):
        ts_array['ts1'].loc[0]=current_ts
        prev_ts=ts_array['ts0'].loc[0]
        if current_ts>prev_ts and current_ts>5:
            ts_array['att'].loc[0]=4/3
        elif current_ts>1.2*prev_ts and current_ts<6:
            ts_array['att'].loc[0]=4/3
        elif current_ts<0.66*prev_ts:
            ts_array['att'].loc[0]=0.5
        else:
            ts_array['att'].loc[0]=1
    return ts_array


#%% Confidence
from conf_list import conf_pd



def att_scaling_conf(conf_value):
    alpha=0.05/(1+0.05*(conf_value-4.5))



def conf_evol(conf_value):
    if conf_value>5:
        z=(conf_value-5)
        return 0.0001251*z*z*z*z-0.0015432*z*z*z+0.007*z*z-0.0426*z+conf_value
    else:
        z=(conf_value-5)
        return 0.002082*z*z*z*z-0.0042388*z*z*z-0.014876*z*z-0.050678*z+conf_value      

def conf_matches(scored_goals,conceded_goals,conf_value):
    conf_multiplier=conf_pd[scored_goals].loc[conceded_goals]
    return conf_value*conf_multiplier

def sc_scaling(conf_actual,att_actual,conf_now):
    att45=att_actual/(1+0.05*(conf_actual-4.5))
    att_now=att45*(1+0.05*(conf_now-4.5))
    return att_now

def slider_effect_scaling(slider_setting):
    #slider setting as a percentage, -100 to 100
    if slider_setting>0:
        return 1+0.000875*slider_setting
    else:
        return 1+0.001175*slider_setting

def confidence_evolution(ts_data,match_datetimes,match_type,\
                         goals_for,\
                         goals_against,\
                         campaign_season_start,\
                         season_start_date=season_start_date84,\
                         next_match_date=datetime.now()):
    
    #%%    
    #import reset times
    
    cc_reset,quali_reset,wc_reset,wcr2_reset,wcr3_reset,wcr4_reset=ts_reset_times(season_start_date)
    
    cf_integer=ts_data['confidence'].values
    
    cf_evol=[]
    dates_evol=[]
    cf_atmatch=[]
    cf_integer_match=[]
    
    current_campaign=campaign_season_start.values[-1]

    match_dates=[match_datetime.date() for match_datetime in match_datetimes]

    curr_date=season_start_date
    current_cf=5#initial cf level
    curr_match_num=len(match_datetimes)-1
    #curr_match_num=0
    while 1:
        match_types_season=match_type[campaign_season_start==current_campaign]#isolate matches for current campaign only
        
        if curr_date<cc_reset:
            if curr_date in match_dates:
                cf_atmatch.append(None)
                cf_integer_match.append(None)
                print(curr_date)
                curr_match_num=curr_match_num-1#remember list is backwards
        
        
        if curr_date>=cc_reset:
           #daily update
           current_cf=conf_evol(current_cf) 
           

           
           #do resets
           if (curr_date-quali_reset).days%224==0 and 'W' in match_types_season.values:
               current_cf=5
               #print('wc quali reset')
           elif (curr_date-wc_reset).days%224==0 and 'WC' in match_types_season.values:
               current_cf=5
               #print('wc reset')
           elif (curr_date-wc_reset).days%224==0 and 'NC' in match_types_season.values:
               current_cf=5
               #print('wc reset')
           elif (curr_date-wcr2_reset).days%224==0 and 'WC2' in match_types_season.values:
               current_cf=current_cf-0.8*(current_cf-5)
               #print('wc rest round 2')
           elif (curr_date-wcr3_reset).days%224==0 and 'WC3' in match_types_season.values:
               current_cf=current_cf-0.6*(current_cf-5)
           elif (curr_date-wcr4_reset).days%224==0 and 'WC4' in match_types_season.values:
               current_cf=current_cf-0.4*(current_cf-5)
           elif (curr_date-wcr4_reset).days%224==0 and (datetime.now().date()-curr_date).days<7:
               current_cf=current_cf-0.4*(current_cf-5)  
           elif (curr_date-cc_reset).days%224==0:
               current_cf=5

           #changes from matches:
           #print(curr_date)
           cf_evol.append(current_cf)     
           dates_evol.append(curr_date)
           
           if curr_date in match_dates:
               #print('match '+str(curr_date))
               mtype=match_type[curr_match_num]
               mdate=match_dates[curr_match_num]
               #print('match '+str(mdate))

               if mtype!='F':
                   
                   
                   cf_atmatch.append(current_cf)#record CF BEFORE the match
                   cf_integer_match.append(cf_integer[curr_match_num])
                   
                   #correct cf
                   scored_goals=goals_for[curr_match_num]
                   conceded_goals=goals_against[curr_match_num]   
                   print(current_cf)
                   print(scored_goals)
                   print(conceded_goals)
                   current_cf=conf_matches(scored_goals,conceded_goals,current_cf)
                   print(current_cf)
                   cf_evol.append(current_cf)
                   print('match '+str(mdate))
               else:
                   cf_atmatch.append(None)
                   cf_integer_match.append(None)
                   
                   print('friendly match '+str(mdate))
               
               curr_match_num=curr_match_num-1#remember list is backwards
               if curr_match_num>-1:
               #if curr_match_num<len(match_dates):    
                   current_campaign=campaign_season_start[curr_match_num]#change the campaign number for next iteration
           else:
               #print('no match '+str(curr_date))
               pass
        curr_date=curr_date+timedelta(days=1)
        
        print(str(curr_date))
        #if curr_date==season_start_date+timedelta(days=224):
            #break
        if curr_date>next_match_date.date():
            print('reached present day')
            break
#%%
               
    return cf_evol, cf_atmatch,cf_integer_match
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



    

"""            
def get_nt_match_ratings(nt_match_id,debug_on=0):
 
    driver.get(url='https://www.hattrick.org/en/Club/Matches/Match.aspx?matchID=' + str(nt_match_id) + '&SourceSystem=HTOIntegrated')
    time.sleep(5)
    table_head = driver.find_elements(By.TAG_NAME, 'th')
    cells = driver.find_elements(By.TAG_NAME, 'td')
    match_events=driver.find_elements(By.TAG_NAME,'ht-matchevent')
    try:
        match_data={
            'Match Datetime' : datetime.strptime(driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[2]/span[1]').text,'%d/%m/%Y %H.%M'),
            'Match Type': driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[1]').text
            }
    except ValueError:
        match_data={
            'Match Datetime' : datetime.strptime(driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[2]/span[1]').text,'%d.%m.%Y %H:%M'),
            'Match Type': driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[1]').text
            }        
    except NoSuchElementException:
        
        print('retrying load of match data')
        driver.refresh()
        driver.get(url='https://www.hattrick.org/en/Club/Matches/Match.aspx?matchID=' + str(nt_match_id) + '&SourceSystem=HTOIntegrated')
        time.sleep(5)
        table_head = driver.find_elements(By.TAG_NAME, 'th')
        cells = driver.find_elements(By.TAG_NAME, 'td')
        match_events=driver.find_elements(By.TAG_NAME,'ht-matchevent')
        try:
            match_data={
                'Match Datetime': datetime.strptime(driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[2]/span[1]').text,'%d/%m/%Y %H.%M'),
                'Match Type': driver.find_element(By.XPATH,'//*[@id="ngMatch"]/div/div/div[2]/div[5]/div[1]/div[2]/div[2]/div/p[1]').text
                }        
        except NoSuchElementException:
            #print('full page source')
            #print(driver.page_source)
            pass
    try:
        table_head[2].text
    except IndexError:
        print('something wrong with match import, printing page source')
        print(table_head)
    
    print('processing '+table_head[2].text+' vs '+ table_head[4].text)
    
    
    #get score
    result_line=[mevc.text for mevc in match_events if 'The match ends' in mevc.text]
    
    #for walkover
    # print([mevc.text for mevc in match_events])
    if len(result_line)!=1:
        score_home=0
        score_away=0
        wo_line=[mevc.text for mevc in match_events if "The game couldn't be played as the home" in mevc.text\
                 or "The game couldn't be played and the referee had to declare the away" in mevc.text\
                 or "The home side conceded a walk over" in mevc.text\
                 or "The home supporters were embarrassed" in mevc.text]
        home_crowd_line=[mevc.text for mevc in match_events if "The home crowd was not amused!" in mevc.text]
            
        #print(wo_line)
        if len(wo_line)==1 or len(home_crowd_line)==1:
            score_home=0
            score_away=5
        else:
            wo_line=[mevc.text for mevc in match_events if "The game couldn't be played as the away" in mevc.text or "The game couldn't be played and the referee had to declare the home" in mevc.text or "The visitors weren't able to produce at least 9 players" in mevc.text]
        away_crowd_line=[mevc.text for mevc in match_events if "The away crowd was not amused!" in mevc.text or 'The home supporters jeered the visiting team when it was announced that the away side had failed to select 9 players in their lineup' in mevc.text]

        if len(wo_line)==1 or len(away_crowd_line)==1:
            score_home=5
            score_away=0 

            
        
    else:
        score_home,score_away=result_line[0].split('The match ends ')[1].strip('.').split(' - ')
    #find 'average goals'
    cells_text=[cells[i].text for i in range(len(cells))]
    if 'Average goals' not in cells_text:
        print('possible WO, skipping')
        team_A = {
            'Team name': table_head[2].text,
            'Midfield':-1,
            'Right defence': -1,
            'Central defence': -1,
            'Left defence': -1,
            'Right attack': -1,
            'Central attack': -1,
            'Left attack': -1,
            'ISP defence': -1,
            'ISP attack': -1,
            'Tactic': 'WO',
            'Tactic skill': 0,
            'Total exp': -1,
            'Style of play': 0,
            'Average goals': -1,
            'Actual goals' : int(score_home),
            'Defender_number' : 0,
            'Midfielder_number' : 0,
            'Forward_number' : 0
        }        
        
        team_B = {
            'Team name': table_head[4].text,
            'Midfield':-1,
            'Right defence': -1,
            'Central defence': -1,
            'Left defence': -1,
            'Right attack': -1,
            'Central attack': -1,
            'Left attack': -1,
            'ISP defence': -1,
            'ISP attack': -1,
            'Tactic': 'WO',
            'Tactic skill': 0,
            'Total exp': -1,
            'Style of play': 0,
            'Average goals': -1,
            'Actual goals' : int(score_away),
            'Defender_number' : 0,
            'Midfielder_number' : 0,
            'Forward_number' : 0
        }               
        
        
        
        
        
        
        return team_A, team_B ,match_data
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
        'Average goals': float(cells_text[avggoal_index-1].replace(',','.')),
        'Actual goals' : int(score_home)
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
        'Average goals': float(cells_text[avggoal_index+1].replace(',','.')),
        'Actual goals' : int(score_away)
    }
    
    
    spans = driver.find_elements(By.TAG_NAME, 'span')
    match_text = ''
    for i in range(70, 120):  
        match_text += (spans[i].text)
    
    formations_text = re.findall("[2-5]-[2-5]-[0-3]", match_text)
    print(formations_text)
    if len(formations_text)==0:
        for i in range(121, 160):
            match_text += (spans[i].text)
            formations_text = re.findall("[2-5]-[2-5]-[0-3]", match_text)

    home_team_formation = formations_text[0]
    if len(formations_text)>1:
        away_team_formation = formations_text[1]
    else:
        away_team_formation = formations_text[0]
        
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
    
def season_idcol_create(match_datetimes,season_start_date84=datetime(2023,3,6)):
    pass
    season_ids=[]
    for m in match_datetimes:
        td=m-season_start_date84
        tdays=td.days
        tseas=tdays//(16*7*2)
        seas=84+2*tseas
        season_ids.append(seas)
    return season_ids
"""        
        
        
        
        
        
    #%%
if __name__=='__main__':    
    """
    nt_match_id = 31515894
    
    team_A, team_B, match_data = get_nt_match_ratings(nt_match_id)
    print('match data = '+str(match_data))
    print('Team A = ', team_A)
    print('Team B = ',  team_B)
    """
    
    

    seasons=[90,89,88,87,86,85,84]
    if import_from_remote==True:
                    
        try:
            access_token
        except:
            print('no object chpp active')
            
            from hattrick_auth import ht_auth

            access_token=ht_auth()
        from hattrick_auth import chpp_object_create
        chpp=chpp_object_create(access_token)   
        try:
            #nt_match_ids=get_NT_match_IDs(nt_id, seasons)
            nt_match_ids=get_match_list(chpp,nt_id,seasons)
        except:
            print('no connection to site')
            

        
        team_a_list=[]
        team_b_list=[]
        match_list=[]
        for ntmid in nt_match_ids:
            #team_A, team_B,match_data = get_nt_match_ratings(ntmid)
            team_A,team_B,match_data=get_match_data_chpp(chpp,ntmid)
            if team_A is not None:
                team_a_list.append(team_A)
                team_b_list.append(team_B)
                match_list.append(match_data)
            
        
        
        
        
        home_ratings=pd.DataFrame([a for a in team_a_list if a is not None])
        away_ratings=pd.DataFrame([b for b in team_b_list if b is not None])
        away_ratings=away_ratings.reindex(home_ratings.columns,axis=1)
        
        matches_pd=pd.DataFrame([m for m in match_list if m is not None])
        #home_ratings.to_csv('home_ratings_backup.csv',index=False)
        #away_ratings.to_csv('away_ratings_backup.csv',index=False)
        #matches_pd.to_csv('matches_data_backup.csv',index=False)
    else:
        pass
        #home_ratings=pd.read_csv('home_ratings_backup.csv',index_col=None)
        #away_ratings=pd.read_csv('away_ratings_backup.csv',index_col=None)
        #matches_pd=pd.read_csv('matches_data_backup.csv',index_col=None)
        #matches_pd['Match Datetime']=[datetime.strptime(d.split('+')[0],'%Y-%m-%d %H:%M:%S') for d in matches_pd['Match Datetime']]
        
    #%% FORM AND SAVE PANDAS DF, WITH COUNTRY OF INTEREST ON THE LEFT
    if import_from_remote:
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
        #overall_ratings_pd.sort_values(by='Match Datetime',axis=0,ascending=False,inplace=True)
        
        overall_ratings_pd.columns=overall_ratings_pd.columns[:3]\
            .union(home_ratings.columns,sort=False).union(pd.Series(['HomeOrAway']),sort=False)\
            .union(pd.Series(home_ratings.columns).apply(add_),sort=False).union(pd.Series(['HomeOrAway_']),sort=False)
    
    if not import_from_remote:
        overall_ratings_pd=pd.read_csv(str(nt_id)+'_ratings_data.csv')
        for col in overall_ratings_pd.columns:
            udroplist=[]
            if 'Unnamed' in col:
                udroplist.append(col)
            overall_ratings_pd=overall_ratings_pd.drop(udroplist,axis=1)
        try:
            overall_ratings_pd['Match Datetime']=[datetime.strptime(d.split('+')[0],'%m/%d/%Y %H:%M') for d in overall_ratings_pd['Match Datetime']]
        except ValueError:
            overall_ratings_pd['Match Datetime']=[datetime.strptime(d.split('+')[0],'%Y-%m-%d %H:%M:%S') for d in overall_ratings_pd['Match Datetime']]
            
    
    #add abbreviations:
    opponents_short=[]
    type_short=[]
    match_date=[]
    formation=[]
    formation_=[]
    tactic_short=[]
    tactics_short_dict={'(no tactic)':'N','Normal':'N','Counter-attacks':'CA','Pressing':'Pr',\
                        'Play creatively':'PC','Attack in the Middle':'AIM',\
                            'Attack on wings':'AOW','Long shots':'LS','WO':'WO'}
    
    for i in overall_ratings_pd.index:
        row=overall_ratings_pd.loc[i] 
        if row['Team name_']=='Ītyōṗṗyā' or row['Team name_']=='Äªtyoppya':
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Ītyoppya'
        if row['Team name_']=='Azərbaycan':
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Azerbaycan'
        if row['Team name_']=='Österreich':
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Osterreich'
        if row['Team name_']=='Türkiye':
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Turkiye'            
        if row['Team name_']=='Ísland':
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Island'                
        if row['Team name_']=="O'zbekiston":
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Ozbekiston'                
        if row['Team name_']=="España":
            print('replacing invalid string')
            overall_ratings_pd['Team name_'].loc[i]='Espana'                
        if row['Team name_']=="CÃ´te d'Ivoire":
            overall_ratings_pd['Team name_'].loc[i]="Cote d'Ivoire"
        if row['Team name_']=="MÃ©xico":
            overall_ratings_pd['Team name_'].loc[i]="Mexico"
        if row['Team name_']=="LÃ«tzebuerg":
            overall_ratings_pd['Team name_'].loc[i]="Letzebuerg"
        if row['Team name_']=="AlgÃ©rie":
            overall_ratings_pd['Team name_'].loc[i]="Algerie"
        if row['Team name_']=="MagyarorszÃ¡g":
            overall_ratings_pd['Team name_'].loc[i]="Magyaroszag"
        if row['Team name_']=="MoÃ§ambique":
            overall_ratings_pd['Team name_'].loc[i]="Mosambique"


    
    
    for i in overall_ratings_pd.index:
        row=overall_ratings_pd.loc[i]             
        opponents_short.append(row['Team name_'][:3])
        match_date.append(row['Match Datetime'].date())
        formation.append('-'.join(map(str,row[['Defender_number', 'Mid_number', 'Forward_number']].tolist())))
        formation_.append('-'.join(map(str,row[['Defender_number_', 'Mid_number_', 'Forward_number_']].tolist())))
        tactic_short.append(tactics_short_dict[row['Tactic']])
        

    overall_ratings_pd['Opponent']=opponents_short
    overall_ratings_pd['Match Date']=match_date
    overall_ratings_pd['Formation']=formation
    overall_ratings_pd['Formation_']=formation_
    
    overall_ratings_pd['Tactic short']=tactic_short
    #CORRECTIONS OF MF RATING
    
    #correct tactic ratings and name to fit convention
    #try:
    #    overall_ratings_pd=array_clean(overall_ratings_pd)
    #except ValueError:
    #    print('no array cleaning')
        
    #recreate cup rounds:
    campaign_prev=1000000
    rounds_col=[]
    for i in range(overall_ratings_pd.shape[0]-1,-1,-1):
        row=overall_ratings_pd.iloc[i]
        campaign_curr=row['campaign']
        if campaign_curr!=campaign_prev:
            cc_game_counter=0
            wc_game_counter=0
            campaign_prev=campaign_curr
        
        if row['Competition']=='Africa Cup' or\
           row['Competition']=='Asia and Oceania Cup' or\
           row['Competition']=='America Cup' or\
           row['Competition']=='Europe Cup':                   
            if cc_game_counter<10:
                rounds_col.append('CC')
            elif cc_game_counter==10:
                rounds_col.append('CCQF')
            elif cc_game_counter==11:
                rounds_col.append('CCSF')
            elif cc_game_counter==12:
                rounds_col.append('CCF')
            cc_game_counter=cc_game_counter+1
        elif row['Competition']=='World Cup':
            if wc_game_counter<10:
                rounds_col.append('WC1')
            elif wc_game_counter<16:
                rounds_col.append('WC2')
            elif wc_game_counter<19:
                rounds_col.append('WC3')
            elif wc_game_counter<22:
                rounds_col.append('WC4')
            elif wc_game_counter<25:
                rounds_col.append('WC5')
            elif wc_game_counter==25:
                rounds_col.append('WCSF')
            elif wc_game_counter==26:
                rounds_col.append('WCF')
            wc_game_counter=wc_game_counter+1
        elif row['Competition']=='Wildcard':
            rounds_col.append('W')
        elif row['Competition']=='Nations Cup':
            rounds_col.append('NC')
        elif row['Competition']=='Contender League':
            rounds_col.append('CL')
        elif row['Competition']=='Friendly':
            rounds_col.append('F')
    rounds_col.reverse()

    overall_ratings_pd['Match Type']=rounds_col        
            
    #correct for neutral venues
    
    for i in range(overall_ratings_pd.shape[0]):
        matchtype=overall_ratings_pd['Match Type'].loc[i]
        if '3' in matchtype or '4' in matchtype or '5' in matchtype or\
            matchtype in ['CCQF','CCSF','CCF','WCSF','WCF']:
            overall_ratings_pd['HomeOrAway'].iloc[i]='N'
    

    
    overall_ratings_pd.to_csv(str(nt_id)+'_ratings_data.csv')
    
    match_datetimes=pd.Series(overall_ratings_pd['Match Datetime'])
    


    #import team spirits - currently manual
    
    
    #ts_data=ts_data_import(nt_id)
    if import_from_remote_ts:
        try:
            ts_data=ehffutbol_ts_tc(nt_id)
        except:
            rtfile=str(nt_id)+'_ts_data.txt'
            ts_data=raw_text_output_process(rtfile)
            
    else:
        try:
            ts_data=raw_text_output_process(str(nt_id)+'_ts_data.txt')
        except FileNotFoundError:
            ts_data=pd.read_csv(str(nt_id)+'_ts_data.csv')
        try:
            try:
                ts_data['datetime']=[datetime.strptime(d,'%Y-%m-%d') for d in ts_data['datetime']]
            except ValueError:
                ts_data['datetime']=[datetime.strptime(d,'%m/%d/%Y') for d in ts_data['datetime']]
                
        except TypeError:
            pass
    #ts_array=attitude_guess(ts_data,match_datetimes)
    
    dupes=ts_data.duplicated('datetime',keep=False)
    if sum(dupes)>0:
        print('warning: duplicated rows might affect calculation')
        
        ts_data=ts_data.sort_index()
        ts_data=ts_data.drop_duplicates('datetime',keep='first')
            
        
    ts_data.to_csv(str(nt_id)+'_ts_data.csv',index=False)
    ts_data=ts_data.sort_values(by='datetime',ascending=False)
            
    ts_data[ts_data['datetime']>'2023-01-31']

 
    

    ts_array=attitude_guess_ehff(ts_data,match_datetimes,player_drop_events)
    
    
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
    ts=ts_array['ts0']
    attitudes=ts_array['att'].copy()
    
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
            attitudes.loc[attitudes.shape[0]-7]=4/3
            #attitudes.loc[attitudes.shape[0]-40]=1/2            
            #attitudes.loc[attitudes.shape[0]-28]=4/3
            #attitudes.loc[attitudes.shape[0]-7]=4/3
            #attitudes.loc[attitudes.shape[0]-5]=4/3
            #attitudes.loc[attitudes.shape[0]-34]=4/3
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
        if nt_id==3184:
            attitudes.loc[attitudes.shape[0]-5]=4/3              
            attitudes.loc[attitudes.shape[0]-29]=1/2
        if nt_id==3112:
            attitudes.loc[attitudes.shape[0]-7]=4/3  
        if nt_id==3230:
            attitudes.loc[attitudes.shape[0]-7]=4/3
        if nt_id==3025:
            attitudes.loc[attitudes.shape[0]-7]=4/3
        if nt_id==3035:
            attitudes.loc[attitudes.shape[0]-7]=4/3            
            attitudes.loc[attitudes.shape[0]-29]=4/3    
            attitudes.loc[attitudes.shape[0]-69]=4/3   
        if nt_id==3010:
            attitudes.loc[attitudes.shape[0]-68]=1     
        if nt_id==3006:
            attitudes.loc[attitudes.shape[0]-37]=4/3                 
            attitudes.loc[attitudes.shape[0]-39]=4/3
            attitudes.loc[attitudes.shape[0]-49]=4/3
        if nt_id==3234:
            attitudes.loc[attitudes.shape[0]-31]=1/2            
        if nt_id==3200:
            attitudes.loc[attitudes.shape[0]-75]=4/3
            attitudes.loc[attitudes.shape[0]-78]=4/3
        if nt_id==3085:
            attitudes.loc[attitudes.shape[0]-80]=4/3
        if nt_id==3034:                       
            attitudes.loc[attitudes.shape[0]-83]=4/3
        if nt_id==3089:
            attitudes.loc[attitudes.shape[0]-7]=4/3 
            attitudes.loc[attitudes.shape[0]-23]=1/2            
            attitudes.loc[attitudes.shape[0]-29]=1/2
            attitudes.loc[attitudes.shape[0]-79]=4/3  
        if nt_id==3130:
            attitudes.loc[attitudes.shape[0]-7]=4/3
            attitudes.loc[attitudes.shape[0]-46]=4/3
            attitudes.loc[attitudes.shape[0]-83]=4/3  
            
            
                       
    ts_array['att']=attitudes.round(decimals=1)
    ts_evol,ts_atmatch,ts_integer=ts_evolution(match_datetimes=overall_ratings_pd['Match Datetime'],\
                         match_type=overall_ratings_pd['Match Type'],\
                         campaign_season_start=overall_ratings_pd['campaign'],\
                         ts_array=ts_array,\
                         season_start_date=season_start_date84.date(),\
                         player_drop_events=player_drop_events)
        
    cf_evol, cf_atmatch,cf_integer=confidence_evolution(ts_data,match_datetimes=overall_ratings_pd['Match Datetime'],\
                             match_type=overall_ratings_pd['Match Type'],\
                             goals_for=overall_ratings_pd['Actual goals'],\
                             goals_against=overall_ratings_pd['Actual goals_'],\
                             campaign_season_start=overall_ratings_pd['campaign'],\
                             season_start_date=season_start_date84.date(),\
                             next_match_date=datetime.now())
        
        
        
    ts_array['ts_ev']=ts_atmatch
    ts_array['scmd']=scaled_midfields
    ts_array['md']=overall_ratings_pd['Midfield']
    ts_array['Match Datetime']=overall_ratings_pd['Match Date']
    #ts_array[6]=None
    ts_array['type']=overall_ratings_pd['Match Type']
    ts_array['loc']=overall_ratings_pd['HomeOrAway']
    ts_array['frm']=overall_ratings_pd['Formation']
    ts_array['tac']=overall_ratings_pd['Tactic short']
    pd.set_option('display.max_columns', 15)
    
    
    
    curr_ts=ts_evol[-1]
    conf_now=cf_evol[-1]
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
        elif loc in ['A'] and match_venue_forthem=='WCH':
            midr_with_han=midr_withts*derby_away_multiplier
        elif loc in ['H'] and match_venue_forthem=='WCH':
            midr_with_han=midr_withts*derby_away_multiplier/home_multiplier
        else:
            midr_with_han=midr_withts
        if att<0.75:
            #midr_with_attitude=midr_with_han/1.13
            midr_with_attitude=midr_with_han/1.115
        elif att>1.2:
            #midr_with_attitude=midr_with_han/0.87
            midr_with_attitude=midr_with_han/0.8395
        else: 
            midr_with_attitude=midr_with_han
        S.append(midr_with_attitude)
        #break
    
    
    overall_ratings_pd['scaled_midfield']=S     
    ts_array['scmd']=S
    pd.options.display.float_format = "{:,.2f}".format
    #print(ts_array)
    if 'scaled midfield' not in overall_ratings_pd.columns:
        overall_ratings_pd.insert(3,'scaled midfield',S)
    else:
        overall_ratings_pd['scaled midfield']=S   
    pd.options.display.float_format = "{:,.2f}".format
    print(ts_array)    
    
    #same for confidence
    SA=[]
    cf_atmatch.reverse()
    for i in range(overall_ratings_pd.shape[0]):
        attack_ratings=overall_ratings_pd.iloc[i][['Left attack','Central attack','Right attack']]
        cf_then=cf_atmatch[i]
        if cf_then is None:
            SA.append([None,None,None])
            continue
        attack_ratings_scaled=[]
        for attr in attack_ratings:
            attack_ratings_scaled.append(sc_scaling(cf_then,attr,conf_now))

        SA.append(attack_ratings_scaled)
        #break
    #SA.reverse()
    
    overall_ratings_pd[['sc_la','sc_ca','sc_ra']]=SA     
    
    
    for cname in ['sc_la','sc_ca','sc_ra']:
        overall_ratings_pd.insert(4, cname, overall_ratings_pd.pop(cname))


    #SAVE AND UPLOAD   
    
    
    overall_ratings_pd.to_csv(str(nt_id)+'_ratings_data.csv')
    
    
    github_upload(str(nt_id)+'_ratings_data.csv')
    


        #pd.DataFrame([w]).to_csv('sillydir/'+str(w)+'.csv')
        #github_upload('sillydir/'+str(w)+'.csv',repo='test-')
    
    
    
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
    



