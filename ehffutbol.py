# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 00:36:50 2024

@author: Tyufik
"""

from bs4 import BeautifulSoup as bs
import requests
import os
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from time import strptime

# set options to be headless
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)


def ehffutbol_ts_tc(nt_id=3172):
    ts_array=[]
    
    #process initial page
    page_url = 'https://ehf.futbol/EHFEuro/Team.aspx?teamid='+str(nt_id)
    driver.get(page_url)
    time.sleep(5)
    D=driver.find_elements(By.TAG_NAME,'option')
    Months=[]
    Years=[]
    curr_year_in_list=0
    for H in D:
        print(H.text)
        print(H.text.isdigit())
        if H.text.isdigit():
            Years.append(H)
        else:
            Months.append(H)
    
    
    E=driver.find_elements(By.ID,"FeaturedContent_MainContentYouthChampionship_Calendar1")
    for K in E:
        
        tstc=K.get_attribute('innerText')
        print(tstc)
        R=raw_tstc_output_process(tstc)
        rs_array=R
    while 1:
        #now click for past data
        Mpress=Months[-1]
        if Mpress.text=='December':
            #change year
            curr_year_in_list=curr_year_in_list+1
            Ypress=Years[curr_year_in_list]
            Ypress.click()
        Mpress.click()
        time.sleep(5)
        print('NEW MONTH')
        
        D=driver.find_elements(By.TAG_NAME,'option')
        Months=[]
        Years=[]
        for H in D:
            print(H.text)
            print(H.text.isdigit())
            if H.text.isdigit():
                Years.append(H)
            else:
                Months.append(H)
        
        
        E=driver.find_elements(By.ID,"FeaturedContent_MainContentYouthChampionship_Calendar1")
        for K in E:
           
            tstc=K.get_attribute('innerText')
            print(tstc)
            R=raw_tstc_output_process(tstc)
            ts_array.extend(R)
    return ts_array


def raw_tstc_output_process(r):
    rlist=r.strip().split('TS')
    
    
    R=[]
    r0=rlist[0]
    month_year=r0.split('\n')[0].split('\t')
    month_prev=month_year[0]
    month=month_year[1].split()[0]
    year=int(month_year[1].split()[1])
    month_next=month_year[2]
    curr_date=int(re.findall(r'\d+', r0)[-1])
    if curr_date==1:
        curr_month=month
    else:
        curr_month=month_prev
    for i in range(len(rlist)):
        if i>0:
            currec=rlist[i]
            if 'TC' in currec:
                currec_tc=currec.split('TC')
                current_ts=int(re.findall(r'\d+', currec_tc[0])[0])
                tc_string=re.findall(r'\d+', currec_tc[1])
                current_tc=int(tc_string[0])
                
                if curr_date==1 and curr_month==month_prev:
                    curr_month=month
                elif curr_date==1 and curr_month==month:
                    curr_month=month_next
                if curr_month==month_prev and curr_month=='December':
                    curr_year=year-1
                else:
                    curr_year=year
                
                dtime=datetime(curr_year,strptime(curr_month[:3],'%b').tm_mon,curr_date)
                R.append([dtime,current_ts,current_tc])
                if len(tc_string)>1:
                    next_date=int(tc_string[1])
                    curr_date=next_date
                
    return R
                
                
if __name__=='__main__':
    ts_array=ehffutbol_ts_tc(nt_id=3172)        
    
"""
      January	February 2024	March

Mon	Tue	Wed	Thu	Fri	Sat	Sun
29
TS: 6
TC: 3	30
TS: 6
TC: 3	31
TS: 6
TC: 4	1
TS: 6
TC: 4	2
TS: 6
TC: 4	3
TS: 8
TC: 3	4
TS: 8
TC: 3
5
TS: 8
TC: 3	6
TS: 8
TC: 3	7
TS: 7
TC: 3	8
TS: 7
TC: 3	9	10	11
12	13	14	15	16	17	18
19	20	21	22	23	24	25
26	27	28	29	1	2	3
4	5	6	7	8	9	10


<table id="FeaturedContent_MainContentYouthChampionship_Calendar1" cellspacing="0" cellpadding="2" title="Calendar" style="border-width:1px;border-style:solid;width:100%;border-collapse:collapse;">
		<tbody><tr><td colspan="7" style="background-color:#F7F7F7;"><table cellspacing="0" style="width:100%;border-collapse:collapse;">
			<tbody><tr><td style="width:15%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','V8766')" style="color:Black" title="Go to the previous month">January</a></td><td align="center" style="width:70%;">February 2024</td><td align="right" style="width:15%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','V8826')" style="color:Black" title="Go to the next month">March</a></td></tr>
		</tbody></table></td></tr><tr><th align="center" abbr="Monday" scope="col" style="border-style:None;">Mon</th><th align="center" abbr="Tuesday" scope="col" style="border-style:None;">Tue</th><th align="center" abbr="Wednesday" scope="col" style="border-style:None;">Wed</th><th align="center" abbr="Thursday" scope="col" style="border-style:None;">Thu</th><th align="center" abbr="Friday" scope="col" style="border-style:None;">Fri</th><th align="center" abbr="Saturday" scope="col" style="border-style:None;">Sat</th><th align="center" abbr="Sunday" scope="col" style="border-style:None;">Sun</th></tr><tr><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8794')" style="color:Black" title="January 29">29</a><span><hr>TS: 6</span><span><hr>TC: 3</span></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8795')" style="color:Black" title="January 30">30</a><span><hr>TS: 6</span><span><hr>TC: 3</span></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8796')" style="color:Black" title="January 31">31</a><span><hr>TS: 6</span><span><hr>TC: 4</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8797')" style="color:Black" title="February 1">1</a><span><hr>TS: 6</span><span><hr>TC: 4</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8798')" style="color:Black" title="February 2">2</a><span><hr>TS: 6</span><span><hr>TC: 4</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8799')" style="color:Black" title="February 3">3</a><span><hr>TS: 8</span><span><hr>TC: 3</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8800')" style="color:Black" title="February 4">4</a><span><hr>TS: 8</span><span><hr>TC: 3</span></td></tr><tr><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8801')" style="color:Black" title="February 5">5</a><span><hr>TS: 8</span><span><hr>TC: 3</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8802')" style="color:Black" title="February 6">6</a><span><hr>TS: 8</span><span><hr>TC: 3</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8803')" style="color:Black" title="February 7">7</a><span><hr>TS: 7</span><span><hr>TC: 3</span></td><td align="center" style="border-color:Black;border-width:2px;border-style:Solid;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8804')" style="color:Black" title="February 8">8</a><span><hr>TS: 7</span><span><hr>TC: 3</span></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8805')" style="color:Black" title="February 9">9</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8806')" style="color:Black" title="February 10">10</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8807')" style="color:Black" title="February 11">11</a></td></tr><tr><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8808')" style="color:Black" title="February 12">12</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8809')" style="color:Black" title="February 13">13</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8810')" style="color:Black" title="February 14">14</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8811')" style="color:Black" title="February 15">15</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8812')" style="color:Black" title="February 16">16</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8813')" style="color:Black" title="February 17">17</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8814')" style="color:Black" title="February 18">18</a></td></tr><tr><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8815')" style="color:Black" title="February 19">19</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8816')" style="color:Black" title="February 20">20</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8817')" style="color:Black" title="February 21">21</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8818')" style="color:Black" title="February 22">22</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8819')" style="color:Black" title="February 23">23</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8820')" style="color:Black" title="February 24">24</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8821')" style="color:Black" title="February 25">25</a></td></tr><tr><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8822')" style="color:Black" title="February 26">26</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8823')" style="color:Black" title="February 27">27</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8824')" style="color:Black" title="February 28">28</a></td><td align="center" style="width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8825')" style="color:Black" title="February 29">29</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8826')" style="color:Black" title="March 1">1</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8827')" style="color:Black" title="March 2">2</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8828')" style="color:Black" title="March 3">3</a></td></tr><tr><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8829')" style="color:Black" title="March 4">4</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8830')" style="color:Black" title="March 5">5</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8831')" style="color:Black" title="March 6">6</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8832')" style="color:Black" title="March 7">7</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8833')" style="color:Black" title="March 8">8</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8834')" style="color:Black" title="March 9">9</a></td><td align="center" style="background-color:#F7F7F7;width:14%;"><a href="javascript:__doPostBack('ctl00$ctl00$FeaturedContent$MainContentYouthChampionship$Calendar1','8835')" style="color:Black" title="March 10">10</a></td></tr>
	</tbody></table>  
    
    """