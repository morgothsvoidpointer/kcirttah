# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 22:32:37 2023

@author: Tyufik
"""
import re
import pyperclip
import pandas as pd
import os

#S=pyperclip.paste()

#S=pyperclip.waitForPaste()

#pyperclip.waitForNewPaste()

def isFloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def str_between(left,text,right):
    txt=text[text.index(left)+len(left):text.index(right)]
    return txt

def ratings_convert_from_HT_ML(S):
    Tab=S[S.find('[table]'):S.find('[/table]')]
    Tab_emptybrac=string=re.sub("\[.*?\]","[]",Tab)
    Tab_data=Tab_emptybrac.split('[]')
    ratings_dict={}
    rating_current=''
    for i in range(len(Tab_data)):
        
        if Tab_data[i]=='Defence' or Tab_data[i]=='Midfield' or Tab_data[i]=='Attack':
            rating_current=Tab_data[i]
            ratings_dict[rating_current]=[]
        elif isFloat(Tab_data[i]):
            ratings_dict[rating_current].append(float(Tab_data[i]))
    Meta=S[S.find('[/table]'):]
    
    bsplit=Meta.split('[b]')
    for j in range(len(bsplit)):
        jlist=bsplit[j].split('[/b]')
        if jlist[0]=='Formation':
            formation=jlist[1].split()[1]
            (num_defs,num_mids,num_fors)=formation.split('-')
            formation_rating=jlist[1].split()[3]
            formation_rating=formation_rating.strip('()')
        if jlist[0]=='Tactics':
            Tactic=jlist[1].split()[1]
            try:
                tactic_rating=jlist[1].split()[3]
            except IndexError:
                tactic_rating=0
            else:
                tactic_rating=tactic_rating.strip('()')
        if jlist[0]=='Team Attitude':
            team_attitude=jlist[1]
            team_attitude=re.sub('\r\n','',team_attitude)
        if jlist[0]=='Style of play':
            sop_=jlist[1]
            if 'Neutral' in sop_:
                sop=0
            elif 'Defensive' in sop_:
                sop=  0-int(re.findall(r'\d+',sop_)[0])
            elif 'Offensive' in sop_ or 'Attacking' in sop_:
                sop=int(re.findall(r'\d+',sop_)[0])
    return ratings_dict,num_defs,num_mids,num_fors,Tactic,tactic_rating,team_attitude,sop            
            
#
            
            
H=['Match Datetime','Match Type','Team name','scaled midfield','Midfield','Right defence','Central defence','Left defence','Right attack','Central attack','Left attack','ISP defence','ISP attack','Tactic','Tactic skill','Total exp','Style of play','Average goals','Defender_number','Mid_number','Forward_number','HomeOrAway','Team name_','Midfield_','Right defence_','Central defence_','Left defence_','Right attack_','Central attack_','Left attack_','ISP defence_','ISP attack_','Tactic_','Tactic skill_','Total exp_','Style of play_','Average goals_','Defender_number_','Mid_number_','Forward_number_','HomeOrAway_','MT','Opponent','Match Date','Formation','Formation_','Tactic short','scaled_midfield']

H2=['Team name','scaled midfield','Midfield','Right defence','Central defence','Left defence','Right attack','Central attack','Left attack','ISP defence','ISP attack','Tactic','Tactic skill','Defender_number','Mid_number','Forward_number']

def players_convert_from_HT_ML(S):
    Slist=S.split('[b]')
    pos_dict={}
    for i in range(len(Slist)):
        if i==0:
            continue
        else:
            pos_split=Slist[i].split('[/b]')
            pos=pos_split[0]
            playerinfo=pos_split[1].split('\\r\\')
            if len(playerinfo)==1:
                playerinfo=pos_split[1].split('\r\n')
            if len(playerinfo)<3:
              pos_dict[pos]=[None,None,'E']  
              continue
            name=playerinfo[1][1:]
            orientation=playerinfo[0]
            if orientation==' ▲':
                order='D'
            elif orientation==' ▼':
                order='O'
            elif orientation==' ▶':
                order='R'
            elif orientation==' ◀':
                order='L'
            elif orientation==' ':
                order='N'
            spec_string=playerinfo[3]
            if '[i]' not in spec_string:
                spec='Z'
            else:
                spec=str_between('[i]',spec_string,'[/i]')[0]
            pos_dict[pos]=[name,order,spec]
            
            
            
    return pos_dict
S="'[table][tr][th colspan=5]England - San Marino (17/11/2023 20.00) [tournamentmatchid=31658956][/th][/tr][tr][th][/th][th][/th][td align=center][b]GK[/b] \\r\\nR. F. Schafer\\r\\n[playerid=444975587]\\r\\n[/td][th][/th][th][/th][/tr][tr][td align=center][b]RB[/b] ▲\\r\\nJ. Baddeley\\r\\n[playerid=441326510]\\r\\n[i]Quick[/i][/td][td align=center][b]RCD[/b] ▼\\r\\nA. Stewart\\r\\n[playerid=442500073]\\r\\n[i]Technical[/i][/td][td align=center][b]MCD[/b] \\r\\n-[/td][td align=center][b]LCD[/b] ▶\\r\\nG. Goodenough\\r\\n[playerid=444537455]\\r\\n[i]Unpredictable[/i][/td][td align=center][b]LB[/b] \\r\\nN. Bines\\r\\n[playerid=446978691]\\r\\n[i]Quick[/i][/td][/tr][tr][td align=center][b]RW[/b] ▶\\r\\nD. Smith\\r\\n[playerid=443811540]\\r\\n[i]Head[/i][/td][td align=center][b]RIM[/b] \\r\\n-[/td][td align=center][b]MIM[/b] ▼\\r\\nJ. Bygrave\\r\\n[playerid=442455840]\\r\\n[i]Head[/i][/td][td align=center][b]LIM[/b] ▼\\r\\nJ. Longson\\r\\n[playerid=448354184]\\r\\n[i]Head[/i][/td][td align=center][b]LW[/b] ▼\\r\\nM. Johnston\\r\\n[playerid=436779382]\\r\\n[i]Head[/i][/td][/tr][tr][th][/th][td align=center][b]RFW[/b] \\r\\nJ. Catron\\r\\n[playerid=444450481]\\r\\n[i]Unpredictable[/i][/td][td align=center][b]MFW[/b] \\r\\n-[/td][td align=center][b]LFW[/b] \\r\\nP. B. Bost\\r\\n[playerid=437802255]\\r\\n[i]Quick[/i][/td][th][/th][/tr][/table]\\r\\n\\r\\n[table][tr][th align=center colspan=4]Substitutes[/th][/tr][tr][th align=center]Goalkeeper[/th][th align=center]Central Defender[/th][th align=center]Wing back[/th][th align=center]Inner Midfielder[/th][/tr][tr][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][/tr][tr][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][/tr][tr][th align=center]Forward[/th][th align=center]Winger[/th][th align=center]Extra[/th][th rowspan=3][/th][/tr][tr][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][/tr][tr][td align=center]-[/td][td align=center]-[/td][td align=center]-[/td][/tr][/table]\\r\\n\\r\\n[table][tr][th]Captain[/th][th]Set-Pieces[/th][/tr][tr][td align=center]-[/td][td align=center]-[/td][/tr][/table]'"

#Convert input from the two strings into 3 objects - 
#vector for ratings
#vector for specs
#array for presentation


H2=['Team name','scaled midfield','Midfield','Right defence','Central defence','Left defence','Right attack','Central attack','Left attack',\
    'ISP defence','ISP attack','Tactic','Tactic skill','Defender_number','Mid_number',\
        'Forward_number']

#print(metaratings_home)
tactics_abbreviate={}
tactics_abbreviate['Normal']='N'
tactics_abbreviate['(no tactic)']='N'
tactics_abbreviate['Counter-attacks']='CA'
tactics_abbreviate['Counter Attacks']='CA'    
tactics_abbreviate['Long shots']='LS'
tactics_abbreviate['Play creatively']='PC'
tactics_abbreviate['Pressing']='Pr'
tactics_abbreviate['Attack on wings']='AOW'
tactics_abbreviate['Attack in the Middle']='AIM'
    
def ratings_record_create(ratings_dict,num_defs,num_mids,num_fors,Tactic,tactic_rating,sop):
    H2={}
    H2['Team name']=str(num_defs)+str(num_mids)+str(num_fors)+tactics_abbreviate[Tactic]+str(tactic_rating)+'_'+str(sop)   
    H2['scaled midfield']=0
    H2['Midfield']=ratings_dict['Midfield'][0]
    H2['Left defence']=ratings_dict['Defence'][0]
    H2['Central defence']=ratings_dict['Defence'][1]
    H2['Right defence']=ratings_dict['Defence'][2]
    H2['Left attack']=ratings_dict['Attack'][0]
    H2['Central attack']=ratings_dict['Attack'][1]
    H2['Right attack']=ratings_dict['Attack'][2]
    H2['ISP defence']=3+int(num_defs)*2
    H2['ISP attack']=3+int(num_fors)*3
    H2['Tactic']=Tactic
    H2['Tactic skill']=tactic_rating
    H2['Defender_number']=num_defs
    H2['Mid_number']=num_mids
    H2['Forward_number']=num_fors    
    return H2

def specs_record_create(pos_dict):
    pos_dict_array=pd.DataFrame(pos_dict).transpose()
    #print(pos_dict_array)
    return pos_dict_array[2]

def individual_order_record_create(pos_dict):
    pos_dict_array=pd.DataFrame(pos_dict).transpose()
    print(pos_dict_array)
    if pos_dict_array[1].loc['LFW']=='L':
        pos_dict_array[1].loc['LFW']='R'
    return pos_dict_array[1].fillna(value='-')

def listener():
    lineup_received=0
    ratings_received=0
    while 1:
        S=pyperclip.waitForNewPaste().strip()
        print(S[:17])
        if S[:7]=='[table]' and not S[:17]=='[table][tr][th]De':
            lineup_received=1
            pos_dict=players_convert_from_HT_ML(S)
            print('lineup received')
        elif S[:3]=='[b]':
            ratings_received=1
            ratings_dict,num_defs,num_mids,num_fors,Tactic,tactic_rating,team_attitude,sop=ratings_convert_from_HT_ML(S)
            print('ratings received')
        elif S[:17]=='[table][tr][th]De':
            ratings_received=1
            ratings_dict,num_defs,num_mids,num_fors,Tactic,tactic_rating,team_attitude,sop=ratings_convert_from_HT_ML(S)
            print('ratings received')
        else:
            print('do not recognise input')
            continue
        if ratings_received+lineup_received==2:
            ratings_received=0
            lineup_received=0
            H2=ratings_record_create(ratings_dict,num_defs,num_mids,num_fors,Tactic,tactic_rating,sop)
            H3=specs_record_create(pos_dict)
            H4=individual_order_record_create(pos_dict)
            #write to files:
            if os.path.exists('test_ratings.csv'):
                P=pd.read_csv('test_ratings.csv',index_col=False)
                p0=P.shape[0]
            else:
                P=pd.DataFrame()
                p0=0
            if os.path.exists('test_specs.csv'):
                Q=pd.read_csv('test_specs.csv',index_col=False)
                q0=Q.shape[0]
            else:
                Q=pd.DataFrame()
                q0=0
            if os.path.exists('test_individual.csv'):
                R=pd.read_csv('test_individual.csv',index_col=False)
                r0=R.shape[0]
            else:
                R=pd.DataFrame()
                r0=0                
            if p0!=q0:
                print('warning: ratings and specs arrays must have same shape')
            if p0!=r0:
                print('warning: ratings and indiv order arrays must have same shape')

            P=pd.concat([P,pd.DataFrame(H2,index=[H2['Team name']])],axis=0) 
            Q=pd.concat([Q,H3.to_frame().transpose()],axis=0)
            R=pd.concat([R,H4.to_frame().transpose()],axis=0)
            P.to_csv('test_ratings.csv',mode='w',index=False)
            Q.to_csv('test_specs.csv',mode='w',index=False)
            R.to_csv('test_individual.csv',mode='w',index=False)
            print('record written to files')
            
            
#%%            
    
if __name__=='__main__':
    listener()          
