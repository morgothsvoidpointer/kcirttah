# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 16:24:42 2023

@author: Tyufik
"""

import pycel
import os
from pycel import ExcelCompiler
import matplotlib.pyplot as plt
from scipy.stats import poisson
import pandas as pd
import numpy as np
import re

from larry_ht_sim import Team,Match
 
#nt_id=3222

from ht_ratings_export import nt_id

np.set_printoptions(threshold=100000)
pd.option_context('display_max_rows',None,'display_max_columns',100)
pd.options.display.max_colwidth=100
nt_id_eng=3035

mots_not_pic=0#set 1 to return results for MOTS and PIN
#set 0 to return results for PIC and PIN
WLD=2
#2 to return win %'s
#1 to return draw %'s
#0 to return opposition win %'s

if mots_not_pic:
    pic_coeff=1.115
    pic_flag='MOTS'
else:
    pic_coeff=0.0859
    pic_flag='PIC'

current_campaign_season_start=88

filename='htme_sim.xlsx'
excel=ExcelCompiler(os.getcwd()+'/'+filename)

#NEED THESE EVALUATIONS TO MAKE THE CELL MAP FUNCTION
excel.evaluate('simulator!P2')
excel.evaluate('simulator!Q2')
excel.evaluate('simulator!R2')
excel.evaluate('simulator!J2')

#excel_backup=ExcelCompiler(os.getcwd()+'/'+filename)

#from string import ascii_uppercase


ratings_home=[15,15,15,15,14,12.5,10.5]
ratings_away=[8,15,2.5,6,22,20,22]


metaratings_home=[13,11,12.5,8,'(no tactic)']
metaratings_away=[17.75,16.00,12.5,25,'Counter Attacks']
formation_home=['Z']*8+['E']+['Z']+['E']*2+['Z']
formation_away=['E']*3+['Z']*10


Q='Q'
H='H'
Z='Z'
Pnf='Pnf'
Pdim='Pdim'
E='E'
U='U'
formation_home=[Q,Pnf,U,\
H,Z,Z,H,Q,\
E,Z,E,E,Z]

formation_away=[E,E,E,\
H,Q,Pdim,Q,H,\
Z,H,Z,Q,H]

    

def wdl_nicarana(ratings_home,\
                 ratings_away,\
                 metaratings_home,\
                 metaratings_away,\
                 formation_home,\
                 formation_away,\
                 predict_with_spex=False):
    
    if predict_with_spex:

        excel.set_value('simulator!J4','Yes')

        #print('predicting with our inputted spex')
    else:
        excel.set_value('simulator!J4','No')        

    
    home_cells=['D14','E14','F14','E15','D16','E16','F16']
    away_cells=['D18','E18','F18','E19','D20','E20','F20']
    for i in range(len(ratings_home)):
        excel.set_value('simulator!'+home_cells[i],ratings_home[i])
    for i in range(len(ratings_away)):
        excel.set_value('simulator!'+away_cells[i],ratings_away[i])        
    
    #print(metaratings_home)
    tactics_convert={}
    tactics_convert['Normal']='(no tactic)'
    tactics_convert['(no tactic)']='(no tactic)'
    tactics_convert['Counter-attacks']='Counter Attacks'
    tactics_convert['Counter Attacks']='Counter Attacks'    
    tactics_convert['Long shots']='Long Shots'
    tactics_convert['Play creatively']='Play Creatively'
    tactics_convert['Pressing']='Pressing'
    tactics_convert['Attack on wings']='Attack On Wings'
    tactics_convert['Attack in the Middle']='Attack In Middle'
    tactics_convert['WO']='WO'
    
    metaratings_home[4]=tactics_convert[metaratings_home[4]]
    metaratings_away[4]=tactics_convert[metaratings_away[4]]
    #print(metaratings_home)
    
    
    home_cells=['I7','J7','K7','L7','M7']
    away_cells=['I8','J8','K8','L8','M8']
    for i in range(len(metaratings_home)):
        excel.set_value('simulator!'+home_cells[i],metaratings_home[i])
    for i in range(len(metaratings_away)):
        excel.set_value('simulator!'+away_cells[i],metaratings_away[i])  

    home_cells=['J11','K11','L11',\
                'I12','J12','K12','L12','M12',\
                'I13','J13','K13','L13','M13']
    away_cells=['J17','K17','L17',\
                'I18','J18','K18','L18','M18',\
                'I19','J19','K19','L19','M19']
    for i in range(len(formation_home)):
        excel.set_value('simulator!'+home_cells[i],formation_home[i])
    for i in range(len(formation_away)):
        excel.set_value('simulator!'+away_cells[i],formation_away[i])  

    if predict_with_spex==False:
        excel.set_value('simulator!J4','No')
    else:
        excel.set_value('simulator!J4','Yes')    
    
    W=excel.evaluate('simulator!P2')
    D=excel.evaluate('simulator!Q2')
    L=excel.evaluate('simulator!R2')
    
    #print(excel.evaluate('simulator!M8'))
    #print(excel.evaluate('simulator!AB31'))
    
    return W,D,L,excel



def array_clean(ratings_array):
    ratings_array=ratings_array[ratings_array['Tactic short']!='WO'].reset_index()
    
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

            elif 'divine' in C4[c]:
                divin=re.search(r'\d+', C4[c]+'0').group()
                
                C4[c]=20+int(divin)
    for c,i in enumerate(C4):
        C4[c]=int(C4[c])
    ratings_array['Tactic_']=C3
    ratings_array['Tactic skill_']=C4
    return ratings_array
                
def ratings_array_rearrange(ratings_array,\
                            test_ratings,\
                            predict_with_spex=True,\
                            test_specs_array=None,\
                            scale=0,\
                            historic_match_simulation=False):

   #if simulating historic matches, the '_test_ratings' is just the 'ratings_array'
   #with the two blocks of columns interchanged. 
    if historic_match_simulation:
        for col in ratings_array.columns:
            if col[-1]!='_' and col+'_' in ratings_array.columns:
                test_ratings[col]=ratings_array[col+'_']
    
   
   
    num_their_results=ratings_array.shape[0]
    num_our_proposals=test_ratings.shape[0]
    wins_array=np.zeros((num_our_proposals,num_their_results))
    draws_array=np.zeros((num_our_proposals,num_their_results))
    losses_array=np.zeros((num_our_proposals,num_their_results))
    
    wins_array2=np.zeros((num_our_proposals,num_their_results))
    draws_array2=np.zeros((num_our_proposals,num_their_results))
    losses_array2=np.zeros((num_our_proposals,num_their_results))
    
    
    goals_historic_home=[]
    goals_historic_away=[]
    goals_predicted_home=[]
    goals_predicted_away=[]
    

    
    #excel-based predictor
    for j in test_ratings.index:
        for i in ratings_array.index:
            if historic_match_simulation:
                if i!=j:
                    continue
            
            
            #print(i,j)
            row1=ratings_array.loc[i]
            row2=test_ratings.loc[j]
            
            if 'sc_ra' in ratings_array.columns:
                att_lab_r='sc_ra'
                att_lab_c='sc_ca'
                att_lab_l='sc_la'
            else:
                att_lab_r='Right attack'
                att_lab_c='Central attack'
                att_lab_l='Left attack'
            
            if scale==1 and not np.isnan(row1['scaled midfield']):#scaled for pin
                ratings_home=row1[[att_lab_r,\
                                   att_lab_c,\
                                   att_lab_l,\
                                   'scaled midfield',\
                                   'Right defence',\
                                   'Central defence',\
                                   'Left defence']].to_list()
            elif scale==2 and not np.isnan(row1['scaled midfield']):#scaled for PIC
                ratings_home=row1[[att_lab_r,\
                                   att_lab_c,\
                                   att_lab_l,\
                                   'scaled midfield',\
                                   'Right defence',\
                                   'Central defence',\
                                   'Left defence']].to_list()
                ratings_home[3]=ratings_home[3]*pic_coeff#scale for PIC
            else:
                ratings_home=row1[['Right attack', \
                               'Central attack',\
                               'Left attack',\
                               'Midfield',\
                               'Right defence',\
                               'Central defence',\
                               'Left defence']].to_list()            
            #scale for stamina drop to recreate ratings at 0 mins
            
            
            
            for z in range(len(ratings_home)):
                ratings_home[z]=ratings_home[z]/0.985
            
            
            ratings_away=row2[['Right attack', \
                               'Central attack',\
                               'Left attack',\
                               'Midfield',\
                               'Right defence',\
                               'Central defence',\
                               'Left defence']].to_list()
                
                
                
                
            metaratings_home=row1[['ISP defence',\
                                   'ISP attack']].to_list()+[12.5]+\
                             row1[['Tactic skill',\
                                   'Tactic']].to_list()
            metaratings_away=row2[['ISP defence',\
                                   'ISP attack']].to_list()+[12.5]+\
                             row2[['Tactic skill',\
                                   'Tactic']].to_list()
            #formation
            #defenders:
            Z='Z'
            E='E'
            #print(row1)
            num_defs1=row1['Defender_number']
            if num_defs1==2:
                D=[E,Z,E,E,Z]
            elif num_defs1==3:
                D=[Z,E,Z,E,Z]
            elif num_defs1==4:
                D=[Z,Z,E,Z,Z]
            elif num_defs1==5:
                D=[Z]*5
            num_mids=row1['Mid_number']
            if num_mids==2:
                M=[Z,E,E,E,Z]
            elif num_mids==3:
                M=[Z,E,Z,E,Z]
            elif num_mids==4:
                M=[Z,Z,E,Z,Z]
            elif num_mids==5:
                M=[Z]*5 
            num_forwards=row1['Forward_number']
            F=[Z]*int(num_forwards)+[E]*(3-int(num_forwards))
            #with no data on specs, pick a generic combo of specs

            specs_list=['Q','Q','Q','H','H','H','U','U','U','Q']

            formation_list1=F+M+D#forwards first!
            jj=0
            for ii,pl in enumerate(formation_list1):
                if pl==Z:
                    formation_list1[ii]=specs_list[jj]
                    jj=jj+1
            
            num_defs2=row2['Defender_number']
            if num_defs2==2:
                D=[E,Z,E,E,Z]
            elif num_defs2==3:
                D=[Z,E,Z,E,Z]
            elif num_defs2==4:
                D=[Z,Z,E,Z,Z]
            elif num_defs2==5:
                D=[Z]*5
            num_mids=row2['Mid_number']
            if num_mids==2:
                M=[Z,E,E,E,Z]
            elif num_mids==3:
                M=[Z,E,Z,E,Z]
            elif num_mids==4:
                M=[Z,Z,E,Z,Z]
            elif num_mids==5:
                M=[Z]*5  
            num_forwards=row2['Forward_number']
            F=[Z]*int(num_forwards)+[E]*(3-int(num_forwards))
            #with no data on specs, pick a generic combo of specs
            if test_specs_array is None:
                specs_list=['Q','Q','Q','H','H','H','U','U','U','Q']
            else:
                specs_list=test_specs_array.loc[j]
            formation_list2=F+M+D#forwards first!
            jj=0
            for ii,pl in enumerate(formation_list2):
                if pl==Z:
                    formation_list2[ii]=specs_list.iloc[jj]
                    jj=jj+1
            
            formation_home=formation_list1
            formation_away=formation_list2
            #print(metaratings_home)
            W,D,L,excel=wdl_nicarana(ratings_home,\
                             ratings_away,\
                             metaratings_home,\
                             metaratings_away,\
                             formation_home,\
                             formation_away,\
                             predict_with_spex\
                             )
            #print(metaratings_home)
            wins_array[j,i]=W
            draws_array[j,i]=D
            losses_array[j,i]=L
            
            
            #Larry's
            """
            #Team(team_name, mid, rd, cd, ld, ra, ca, la, ispd, ispa, tactic, tactic_skill, number_of_defenders)
            home_team = Team('Home City', 13, 18, 18, 18, 11, 7, 9, 8, 8, "Counter-attacks", 15, 3)
            away_team = Team('Away Utd', 10, 10, 8, 8, 8, 12, 6, 8, 8, "Pressing", 15, 4)
            """
            
            home_team=Team(*tuple(['Home City']+[ratings_home[3]]+\
                ratings_home[4:7]+ratings_home[:3]+\
                row1[['ISP defence','ISP attack','Tactic','Tactic skill']].tolist()+\
                [int(num_defs1)]))
            away_team=Team(*tuple(['Away Utd']+[ratings_away[3]]+\
                ratings_away[4:7]+ratings_away[:3]+\
                row2[['ISP defence','ISP attack','Tactic','Tactic skill']].tolist()+\
                [int(num_defs2)]))

            
            # Set up the match
            game = Match(home_team, away_team)
            
            # Get the xGs and wins
            game.play()   
         
            W2=game.home_win
            D2=game.draw
            L2=game.away_win

            wins_array2[j,i]=W2/100
            draws_array2[j,i]=D2/100
            losses_array2[j,i]=L2/100
            

            if abs(L-L2/100)>0.1:
                print('WARNING - big predictor discrepancy')
                print(ratings_home)
                print(metaratings_home)
                print(ratings_away)
                print(metaratings_away)
                print(L-L2/100)
                print(L)
                print(L2/100)
              
                
                """
            if abs(W-W2/100)>0.01 and\
                row1['Tactic'] not in ['Pressing','Play creatively'] and\
                row2['Tactic'] not in ['Pressing','Play creatively']:
                print(ratings_home)
                print(metaratings_home)
                print(ratings_away)
                print(metaratings_away)
                print(W-W2/100)                
                print(W)
                """         
            #If we are simulating actual past matches, extract and compare goals with ht predictions
            if historic_match_simulation and i==j:
                goals_historic_home.append(row1['Average goals'])
                goals_historic_away.append(row2['Average goals'])
                goals_predicted_home.append(excel.evaluate('simulator!P15'))
                goals_predicted_away.append(excel.evaluate('simulator!R15'))
            
                            
            
    if historic_match_simulation:
        print('home goals real vs historic')
        print(np.array(goals_historic_home)-np.array(goals_predicted_home))
    if historic_match_simulation:
        print('away goals real vs historic')
        print(np.array(goals_historic_away)-np.array(goals_predicted_away)) 
        
    return wins_array,draws_array,losses_array,\
        wins_array2,draws_array2,losses_array2,\
        goals_historic_home,goals_historic_away,goals_predicted_home,goals_predicted_away
            
def results_array_prune(filename='full_ra_withres.csv',filename1=str(nt_id)+'_test_individual.csv',filename2=str(nt_id)+'_test_ratings.csv',filename3=str(nt_id)+'_test_specs.csv'):
    P=pd.read_csv(filename,index_col=False)
    means=[]
    for col in P.columns:
        if col[0] in ['2','3','4','5']:
            means.append(P[col].mean())
        else:
            means.append(None)
    means_actual=[m for m in means if m is not None]   
    todel=[]
    todel_ind=[]
    ma=0
    if len(means_actual)>5:
        for c,m in enumerate(means):
            if m is None:
                continue
            else:
                if m<np.mean(means_actual)-0.05:
                   todel.append(P.columns[c])
                   todel_ind.append(ma)
                   print(str(P.columns[c])+' removed')
                ma=ma+1
                
        P.drop(todel,axis=1,inplace=True)
        P.to_csv(filename,index=False)
        for fname in [filename1,filename2,filename3]:
            Pz=pd.read_csv(fname,index_col=False)
            Pz.drop(P.index[todel_ind],inplace=True)      
            Pz.to_csv(fname,index=False)
    else:
        print('not enough results generated, nothing removed')

def results_array_drop(name,filename='full_ra_withres.csv'):
    P=pd.read_csv(filename,index=False)
    P.drop([name],axis=1)      
    P.to_csv(filename,index=False)


def results_array_drop_last(filename='full_ra_withres.csv',filename1=str(nt_id)+'_test_individual.csv',filename2=str(nt_id)+'_test_ratings.csv',filename3=str(nt_id)+'_test_specs.csv'):
    P=pd.read_csv(filename,index=False)
    P.drop([P.columns[-1]],axis=1)      
    P.to_csv(filename,index=False)
    for fname in [filename1,filename2,filename3]:
        Pz=pd.read_csv(fname,index=False)
        Pz.drop(P.tail(1).index,inplace=True)      
        Pz.to_csv(fname,index=False)


if __name__=='__main__':
    
    
    pass

    #%%
    W,D,L,excel=wdl_nicarana(ratings_home,\
                     ratings_away,\
                     metaratings_home,\
                     metaratings_away,\
                     formation_home,\
                     formation_away\
                     )


    print('test run W/D/L')
    print(W)
    print(D)
    print(L)
    
    
    #compare with Larry's

    
    
    #import ratings array
    #try:
    #    ratings_array=array_clean(pd.read_csv(str(nt_id)+'_ratings_data.csv'))
    #except ValueError:
    ratings_array=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    ratings_array=ratings_array[ratings_array['Tactic short']!='WO'].reset_index()
    if 'Unnamed: 0' in ratings_array.columns:
        ratings_array=ratings_array.drop('Unnamed: 0',axis=1)
    curr_campaign=max(ratings_array['campaign'])
    
    #ratings_array_eng=array_clean(pd.read_csv(str(nt_id_eng)+'_ratings_data.csv'))
    
    #calculate number of matches since season start
    curr_season=max(ratings_array['campaign'])
    
    #calculate in order to be able to isolate matches from current campaign only
    matches_since_season_start=sum(ratings_array['campaign']==curr_season)

    #calculate in order to be able to isolate matches from current campaign only
    matches_since_previous_start=sum(ratings_array['campaign']==curr_season)+sum(ratings_array['campaign']==curr_season-2)

    
    """
    #To test a set of proposed NT ratings against a full history of matches
    try:
        test_ratings=pd.read_csv('_test_ratings.csv')#IMPORT FILE HERE!!!!
    except FileNotFoundError:
        #if file does not exist, use template to create it
            
        PTR_label=['Team name','scaled midfield','Midfield','Right defence','Central defence',\
         'Left defence','Right attack','Central attack','Left attack','ISP defence',\
         'ISP attack','Tactic','Tactic skill','Defender_number','Mid_number','Forward_number']
        PTR=pd.DataFrame([1]*len(PTR_label)).transpose()

        PTR.columns=PTR_label
        PTR['Team name'].loc[0]='dummy'        
        PTR['Tactic'].loc[0]='(no tactic)'
        
        PTR.to_csv('_test_ratings.csv')
        test_ratings=pd.read_csv('_test_ratings.csv')
        #handle labels:
            
    for i in range(test_ratings.shape[0]):
        if test_ratings['Team name'].iloc[i] in test_ratings['Team name'].iloc[:i].values.tolist():
            test_ratings['Team name'].iloc[i]=test_ratings['Team name'].iloc[i]+'_'+str(i)
    try:
        test_specs_array=pd.read_csv('_test_specs.csv')
    except FileNotFoundError:
        pd.DataFrame(['Z']*10+['E']*3).transpose().to_csv('_test_specs.csv')
        test_specs_array=pd.read_csv('_test_specs.csv')
    """     
    
    test_ratings=pd.read_csv(str(nt_id)+'_test_ratings.csv')#ratings file  
    test_individual_orders=pd.read_csv(str(nt_id)+'_test_individual.csv')#indiv orders - only for display
    test_specs_array=pd.read_csv(str(nt_id)+'_test_specs.csv')#specs file
    test_ratings_labels=test_ratings['Team name'].tolist()#labels for the proposed lineups
    
    #test_ratings.to_csv('_test_ratings.csv')
    
    
    
    
    res_pin=ratings_array_rearrange(ratings_array,\
                            test_ratings=test_ratings,\
                                predict_with_spex=True,\
                                test_specs_array=test_specs_array,\
                                    scale=1)
    
    res_pic=ratings_array_rearrange(ratings_array,\
                            test_ratings=test_ratings,\
                                predict_with_spex=True,\
                                test_specs_array=test_specs_array,\
                                    scale=2)
    
#%%        
        
        
    #examine
    debug_result_examine=0
    def result_examine(res,ratings_array,test_ratings_labels,\
                       averages_only=False,matches_since_season_start=matches_since_season_start):
        
    
        
        
        
        res_=pd.DataFrame(res.transpose())
        res_.columns=test_ratings_labels
        if debug_result_examine:
            print(res_)
        #res_.columns=[]
        ratings_array_withresult=pd.concat([ratings_array,res_],axis=1)
        if debug_result_examine:
            print(ratings_array_withresult)
        #save relevant parts of ratings array
        ratings_array_tosave=ratings_array_withresult[['scaled midfield','Midfield','Right defence',\
        'Central defence', 'Left defence', 'Right attack', 'Central attack',\
        'Left attack','Tactic','Tactic skill','MT','Opponent']+test_ratings_labels]
        ratings_array_tosave=ratings_array_tosave[ratings_array_tosave['MT']!='F']  
        
        ratings_array_tosave.to_csv('full_ra_withres.csv')
        
        
        ratings_array_show=ratings_array_withresult[['MT','Tactic','Opponent']+test_ratings_labels]

        #remove all friendly results
        ratings_array_compet=ratings_array_show[ratings_array_show['MT']!='F'] 
        print(ratings_array_compet)
        ratings_array_compet.columns=['MT','Tactic','Opponent']+test_ratings_labels
        
        ratings_array_ca=ratings_array_compet[ratings_array_compet['Tactic']=='Counter-attacks']
        ratings_array_no=ratings_array_compet[(ratings_array_compet['Tactic']=='(no tactic)')\
                        | (ratings_array_compet['Tactic']=='Attack in the Middle')\
                        | (ratings_array_compet['Tactic']=='Attack on wings')]

        ratings_array_ls=ratings_array_compet[ratings_array_compet['Tactic']=='Long Shots']
        
        ratings_array_pr=ratings_array_compet[ratings_array_compet['Tactic']=='Pressing']

        ratings_array_pc=ratings_array_compet[ratings_array_compet['Tactic']=='Play creatively']

        if averages_only==False:
            print('comparison vs CA')
            print(ratings_array_ca[['MT','Opponent']+test_ratings_labels])
            
            print('comparison vs normal')
            print(ratings_array_no[['MT','Opponent']+test_ratings_labels])

            print('comparison vs longshots')
            print(ratings_array_ls[['MT','Opponent']+test_ratings_labels])
            
            
            print('comparison vs press')
            print(ratings_array_pr[['MT','Opponent']+test_ratings_labels])        
    
            print('comparison vs pc')
            print(ratings_array_pc[['MT','Opponent']+test_ratings_labels])


        #AVERAGES
        ca_avs=ratings_array_ca[test_ratings_labels].mean(axis=0)
        norm_avs=ca_avs=ratings_array_no[test_ratings_labels].mean(axis=0)  
        ls_avs=ratings_array_ls[test_ratings_labels].mean(axis=0)
        pc_avs=ratings_array_pc[test_ratings_labels].mean(axis=0)
        pr_avs=ratings_array_pr[test_ratings_labels].mean(axis=0)
        
        """
        print('average vs ca:')
        print(ca_avs)
        print('average vs normal')
        print(norm_avs)
        if not np.isnan(pc_avs.iloc[0]):
            print('average vs pc')
            print(pc_avs)
        if not np.isnan(pr_avs.iloc[0]):
            print('average vs press')
            print(pr_avs)        
        if not np.isnan(ls_avs.iloc[0]):
            print('average vs longshots')
            print(ls_avs)
        """

        """
        m=matches_since_season_start
        #print(test_ratings_labels)
        #RECENT AVERAGES
        ca_avs=ratings_array_ca[test_ratings_labels].loc[:m].mean(axis=0)
        print('_test')
        print(ratings_array_ca[test_ratings_labels].loc[:m])
        norm_avs=ca_avs=ratings_array_no[test_ratings_labels].loc[:m].mean(axis=0)
        ls_avs=ratings_array_ls[test_ratings_labels].loc[:m].mean(axis=0)
        pc_avs=ratings_array_pc[test_ratings_labels].loc[:m].mean(axis=0)
        pr_avs=ratings_array_pr[test_ratings_labels].loc[:m].mean(axis=0)
        
        
        print('this campaign average vs ca:')
        print(ca_avs)
        print('this campaign average vs normal')
        print(norm_avs)

        if not np.isnan(ls_avs.iloc[0]):
            print('this campaign average vs press')
            print(ls_avs) 

        if not np.isnan(pc_avs.iloc[0]):
            print('this campaign average vs pc')
            print(pc_avs)
        if not np.isnan(pr_avs.iloc[0]):
            print('this campaign average vs press')
            print(pr_avs)
        """
        return ratings_array_ca,ratings_array_no,ratings_array_ls,ratings_array_pc,ratings_array_pr

    #return ratings_array_ca  [test_ratings_label.columns].mean(axis=0) 
        
    def results_present(res_pic,res_pin,ratings_array,test_ratings_labels,test_individual_orders,\
                        matches_since_season_start=matches_since_season_start\
                            ,plot_best=5):
        if plot_best is None:
            plot_best=10000000000
        #transform indiv array
        defence_indiv=[]
        midfield_indiv=[]
        attack_indiv=[]
        
        A=test_individual_orders.values
        for row in A:
            #print(row)
            row_gk=str(row[0])
            row_def=''.join(row[1:6])
            row_mid=''.join(row[6:11])
            row_att=''.join(row[11:14])
            defence_indiv.append(row_def)
            midfield_indiv.append(row_mid)
            attack_indiv.append(row_att)

        
        print('with pic - red')
        ratings_array_pic_ca,ratings_array_pic_no,ratings_array_pic_ls,ratings_array_pic_pc,ratings_array_pic_pr=\
            result_examine(res_pic[WLD],ratings_array,test_ratings_labels)
        print('with pic - larry')
        #result_examine(res_pic[5],ratings_array,test_ratings_labels)    
        
        print('with pin - red')
        ratings_array_pin_ca,ratings_array_pin_no,ratings_array_pin_ls,ratings_array_pin_pc,ratings_array_pin_pr=\
            result_examine(res_pin[WLD],ratings_array,test_ratings_labels)
        print('with pin - larry')
        #result_examine(res_pin[5],ratings_array,test_ratings_labels)
        
        #present the results.
        
    
        
        #AVERAGES PIC FULL
        ca_avs_pic=ratings_array_pic_ca[test_ratings_labels].mean(axis=0).round(4)
        norm_avs_pic=ratings_array_pic_no[test_ratings_labels].mean(axis=0).round(4)
        ls_avs_pic=ratings_array_pic_ls[test_ratings_labels].mean(axis=0).round(4)
        pc_avs_pic=ratings_array_pic_pc[test_ratings_labels].mean(axis=0).round(4)
        pr_avs_pic=ratings_array_pic_pr[test_ratings_labels].mean(axis=0).round(4)
        
    
        m=matches_since_season_start
        m2=matches_since_previous_start
        
        #AVERAGE PIC RECENT
        ca_avs_pic_r=ratings_array_pic_ca[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        norm_avs_pic_r=ratings_array_pic_no[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        ls_avs_pic_r=ratings_array_pic_ls[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        pc_avs_pic_r=ratings_array_pic_pc[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        pr_avs_pic_r=ratings_array_pic_pr[test_ratings_labels].loc[:m].mean(axis=0).round(4)

        #AVERAGE PIC PREVIOUS
        ca_avs_pic_r2=ratings_array_pic_ca[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        norm_avs_pic_r2=ratings_array_pic_no[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        ls_avs_pic_r2=ratings_array_pic_ls[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        pc_avs_pic_r2=ratings_array_pic_pc[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        pr_avs_pic_r2=ratings_array_pic_pr[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        
        
    
        #AVERAGES pin FULL
        ca_avs_pin=ratings_array_pin_ca[test_ratings_labels].mean(axis=0).round(4)
        norm_avs_pin=ratings_array_pin_no[test_ratings_labels].mean(axis=0).round(4)
        ls_avs_pin=ratings_array_pic_ls[test_ratings_labels].mean(axis=0).round(4)
        pc_avs_pin=ratings_array_pin_pc[test_ratings_labels].mean(axis=0).round(4)
        pr_avs_pin=ratings_array_pin_pr[test_ratings_labels].mean(axis=0).round(4)
        

        #AVERAGE pin RECENT
        ca_avs_pin_r=ratings_array_pin_ca[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        norm_avs_pin_r=ratings_array_pin_no[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        ls_avs_pin_r=ratings_array_pin_ls[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        pc_avs_pin_r=ratings_array_pin_pc[test_ratings_labels].loc[:m].mean(axis=0).round(4)
        pr_avs_pin_r=ratings_array_pin_pr[test_ratings_labels].loc[:m].mean(axis=0).round(4)

        #AVERAGE pin RECENT
        ca_avs_pin_r2=ratings_array_pin_ca[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        norm_avs_pin_r2=ratings_array_pin_no[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        ls_avs_pin_r2=ratings_array_pin_ls[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        pc_avs_pin_r2=ratings_array_pin_pc[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        pr_avs_pin_r2=ratings_array_pin_pr[test_ratings_labels].loc[:m2].mean(axis=0).round(4)
        

        
        

            
    
        for df in ratings_array_pic_ca,ratings_array_pic_no,ratings_array_pic_ls,ratings_array_pic_pc,ratings_array_pic_pr:
            ranking=df.reindex(df[test_ratings_labels].mean(axis=0).sort_values(ascending=False).index, axis=1)
            if df.shape[0]==0:
                continue   
            print(pic_flag)
            print(df['Tactic'].iloc[0])
            print(ranking.set_index(df['Opponent']))  
        
            #now, plot the top several options
            coln=0
            for col in ranking:
                if ranking.shape[1]<2:
                    
                    plt.plot(ranking[col],linewidth=0.5,marker='*',label=col)
                else:
                    plt.plot(ranking[col]-ranking[ranking.columns[0]],linewidth=0.5,marker = 'o',label=col)
                plt.title('vs '+df['Tactic'].mode().iloc[0]+' pic, best='+ranking.columns[0])
                plt.xticks(ticks=df['Opponent'].index, labels=df['Opponent'].values,\
                           fontsize=7,rotation = 90)
                coln=coln+1
                if coln>plot_best:
                    break
            plt.legend()
            plt.show()       
         
    
        for df in ratings_array_pin_ca,ratings_array_pin_no,ratings_array_pin_ls,ratings_array_pin_pc,ratings_array_pin_pr:
            ranking=df.reindex(df[test_ratings_labels].mean(axis=0).sort_values(ascending=False).index, axis=1)
            if df.shape[0]==0:
                continue
            print('PIN')
            print(df['Tactic'].iloc[0])
            print(ranking.set_index(df['Opponent']))
            coln=0
            #now, plot the top several options
            for col in ranking:
                if ranking.shape[1]<2:
                    
                    plt.plot(ranking[col],linewidth=0.5,marker='*',label=col)
                else:
                    plt.plot(ranking[col]-ranking[ranking.columns[0]],linewidth=0.5,marker = 'o',label=col)
                plt.title('vs '+df['Tactic'].mode().iloc[0]+' pin, best='+ranking.columns[0])
                plt.xticks(ticks=df['Opponent'].index, labels=df['Opponent'].values,\
                           fontsize=7,rotation = 90)
                coln=coln+1
                if coln>plot_best:
                    break
        
            
            plt.legend()
            plt.show()       
        
        
        
        
        #Make a table
        
        
        from prettytable import PrettyTable
        myTable = PrettyTable(["Tactic","Att","Since"]+test_ratings_labels)
        myTable.add_row(["","",""]+defence_indiv)
        myTable.add_row(["","",""]+midfield_indiv)
        myTable.add_row(["","",""]+attack_indiv)
        if not np.isnan(norm_avs_pic.iloc[0]):
            myTable.add_row(['N',pic_flag,'84']+norm_avs_pic.values.tolist())                  
        if not np.isnan(norm_avs_pic_r.iloc[0]):
            myTable.add_row(['N',pic_flag,str(curr_campaign-2)]+norm_avs_pic_r2.values.tolist())          
        if not np.isnan(norm_avs_pic_r.iloc[0]):
            myTable.add_row(['N',pic_flag,str(curr_campaign)]+norm_avs_pic_r.values.tolist())          
        
        
        if not np.isnan(norm_avs_pin.iloc[0]):
            myTable.add_row(['N','pin','84']+norm_avs_pin.values.tolist())                  
        if not np.isnan(norm_avs_pin_r.iloc[0]):
           myTable.add_row(['N','pin',str(curr_campaign-2)]+norm_avs_pin_r2.values.tolist()) 
        if not np.isnan(norm_avs_pin_r.iloc[0]):
            myTable.add_row(['N','pin',str(curr_campaign)]+norm_avs_pin_r.values.tolist()) 
    
        if not np.isnan(ca_avs_pic.iloc[0]):
            myTable.add_row(['CA',pic_flag,'84']+ca_avs_pic.values.tolist())
        if not np.isnan(ca_avs_pic_r.iloc[0]):
            myTable.add_row(['CA',pic_flag,str(curr_campaign-2)]+ca_avs_pic_r2.values.tolist())
        if not np.isnan(ca_avs_pic_r.iloc[0]):
            myTable.add_row(['CA',pic_flag,str(curr_campaign)]+ca_avs_pic_r.values.tolist())
       
        if not np.isnan(ca_avs_pin.iloc[0]):
            myTable.add_row(['CA','pin','84']+ca_avs_pin.values.tolist())
        if not np.isnan(ca_avs_pin_r.iloc[0]):
            myTable.add_row(['CA','pin',str(curr_campaign-2)]+ca_avs_pin_r2.values.tolist())
        if not np.isnan(ca_avs_pin_r.iloc[0]):
            myTable.add_row(['CA','pin',str(curr_campaign)]+ca_avs_pin_r.values.tolist())
        
        
        if not np.isnan(pr_avs_pic.iloc[0]):
            myTable.add_row(['Pr',pic_flag,'84']+pr_avs_pic.values.tolist())    
        if not np.isnan(pr_avs_pic_r2.iloc[0]):
            myTable.add_row(['Pr',pic_flag,str(curr_campaign-2)]+pr_avs_pic_r2.values.tolist())    
        if not np.isnan(pr_avs_pic_r.iloc[0]):
            myTable.add_row(['Pr',pic_flag,str(curr_campaign)]+pr_avs_pic_r.values.tolist())    
        
        if not np.isnan(pc_avs_pic.iloc[0]):
            myTable.add_row(['PC',pic_flag,'84']+pc_avs_pic.values.tolist())
        if not np.isnan(pc_avs_pic_r2.iloc[0]):
            myTable.add_row(['PC',pic_flag,str(curr_campaign-2)]+pc_avs_pic_r2.values.tolist())
        if not np.isnan(pc_avs_pic_r.iloc[0]):
            myTable.add_row(['PC',pic_flag,str(curr_campaign)]+pc_avs_pic_r.values.tolist())
        
        if not np.isnan(ls_avs_pic.iloc[0]):
            myTable.add_row(['ls',pic_flag,'84']+ls_avs_pic.values.tolist())
        if not np.isnan(ls_avs_pic_r2.iloc[0]):
            myTable.add_row(['ls',pic_flag,str(curr_campaign-2)]+ls_avs_pic_r2.values.tolist())  
        if not np.isnan(ls_avs_pic_r.iloc[0]):
            myTable.add_row(['ls',pic_flag,str(curr_campaign)]+ls_avs_pic_r.values.tolist())  

        if not np.isnan(pr_avs_pin.iloc[0]):
            myTable.add_row(['Pr','pin','84']+pr_avs_pin.values.tolist())    
        if not np.isnan(pr_avs_pin_r2.iloc[0]):
            myTable.add_row(['Pr','pin',str(curr_campaign-2)]+pr_avs_pin_r2.values.tolist())    
        if not np.isnan(pr_avs_pin_r.iloc[0]):
            myTable.add_row(['Pr','pin',str(curr_campaign)]+pr_avs_pin_r.values.tolist())    
        
        if not np.isnan(pc_avs_pin.iloc[0]):
            myTable.add_row(['PC','pin','84']+pc_avs_pin.values.tolist())
        if not np.isnan(pc_avs_pin_r2.iloc[0]):
            myTable.add_row(['PC','pin',str(curr_campaign-2)]+pc_avs_pin_r2.values.tolist())
        if not np.isnan(pc_avs_pin_r.iloc[0]):
            myTable.add_row(['PC','pin',str(curr_campaign)]+pc_avs_pin_r.values.tolist())
        
        if not np.isnan(ls_avs_pin.iloc[0]):
            myTable.add_row(['ls','pin','84']+ls_avs_pin.values.tolist())
        if not np.isnan(ls_avs_pin_r2.iloc[0]):
            myTable.add_row(['ls','pin',str(curr_campaign-2)]+ls_avs_pin_r2.values.tolist())            
        if not np.isnan(ls_avs_pin_r.iloc[0]):
            myTable.add_row(['ls','pin',str(curr_campaign)]+ls_avs_pin_r.values.tolist())            
        print(myTable)    
        
        from PIL import Image, ImageDraw, ImageFont
    
        font = ImageFont.load_default()
        im = Image.new("RGB", (160+90*len(A), 320), "white")
        draw = ImageDraw.Draw(im)
        #font = ImageFont.truetype("FreeMono.ttf", 15)
        font = ImageFont.load_default()
        draw.text((10, 10), str(myTable), font=font, fill="black")
        
        im.show()
        im.save("table.png")
                
        
        #now, do a ranking of results from worst to best, by row mean across the predictions
        #in order to see how our lineups perform vs the most challenging opponent lineups
        
        #AVERAGES PIC FULL
        ca_avs_pic=ratings_array_pic_ca.mean(axis=1,numeric_only=True).round(4)
        #now, sort according to the mean
        ratings_array_pic_ca['av_by_opponent']=ca_avs_pic
        ratings_array_pic_ca.sort_values(by='av_by_opponent',inplace=True)

        #calc worst 5 and worst 10?
        


        norm_avs_pic=ratings_array_pic_no.mean(axis=1,numeric_only=True).round(4)
        #now, sort according to the mean
        ratings_array_pic_no['av_by_opponent']=norm_avs_pic
        ratings_array_pic_no.sort_values(by='av_by_opponent',inplace=True)


        
        norm_avs_pic=ratings_array_pic_no[test_ratings_labels].mean(axis=0).round(4)
        ls_avs_pic=ratings_array_pic_ls[test_ratings_labels].mean(axis=1).round(4)
        pc_avs_pic=ratings_array_pic_pc[test_ratings_labels].mean(axis=1).round(4)
        pr_avs_pic=ratings_array_pic_pr[test_ratings_labels].mean(axis=1).round(4)
        
    
        m=5
        
        #AVERAGE PIC RECENT
        ca_avs_pic_last=ratings_array_pic_ca.loc[ratings_array_pic_ca.index<ratings_array_pic_ca.index.sort_values()[m]]
        ls_avs_pic_last=ratings_array_pic_no.loc[ratings_array_pic_no.index<ratings_array_pic_no.index.sort_values()[m]]
        pc_avs_pic_last=ratings_array_pic_no.loc[ratings_array_pic_no.index<ratings_array_pic_no.index.sort_values()[m]]
        pr_avs_pic_last=ratings_array_pic_no.loc[ratings_array_pic_no.index<ratings_array_pic_no.index.sort_values()[m]]
        no_avs_pic_last=ratings_array_pic_no.loc[ratings_array_pic_no.index<ratings_array_pic_no.index.sort_values()[m]]
 
         
        #AVERAGE PIN RECENT
        ca_avs_pin_last=ratings_array_pin_ca.loc[ratings_array_pin_ca.index<ratings_array_pin_ca.index.sort_values()[m]]
        ls_avs_pin_last=ratings_array_pin_no.loc[ratings_array_pin_no.index<ratings_array_pin_no.index.sort_values()[m]]
        pc_avs_pin_last=ratings_array_pin_no.loc[ratings_array_pin_no.index<ratings_array_pin_no.index.sort_values()[m]]
        pr_avs_pin_last=ratings_array_pin_no.loc[ratings_array_pin_no.index<ratings_array_pin_no.index.sort_values()[m]]
        no_avs_pin_last=ratings_array_pin_no.loc[ratings_array_pin_no.index<ratings_array_pin_no.index.sort_values()[m]]
         
        
        for df in ca_avs_pin_last,no_avs_pin_last:
            ranking=df.reindex(df[test_ratings_labels].mean(axis=0).sort_values(ascending=False).index, axis=1)
            if df.shape[0]==0:
                continue   
            print('PIN')
            print(df['Tactic'].iloc[0])
            print(ranking.set_index(df['Opponent']).transpose())  
        
            #now, plot the top several options
            coln=0
            for col in ranking:
                if ranking.shape[1]<2:
                    
                    plt.plot(ranking[col],linewidth=0.5,marker='*',label=col)
                else:
                    plt.plot(ranking[col]-ranking[ranking.columns[0]],linewidth=0.5,marker = 'o',label=col)
                plt.title('vs '+df['Tactic'].mode().iloc[0]+' pin recent, best='+ranking.columns[0])
                plt.xticks(ticks=df['Opponent'].index, labels=df['Opponent'].values,\
                           fontsize=7,rotation = 90)
                coln=coln+1
                if coln>plot_best:
                    break
            plt.legend()
            plt.show()   
            
        for df in ca_avs_pic_last,no_avs_pic_last:
            ranking=df.reindex(df[test_ratings_labels].mean(axis=0).sort_values(ascending=False).index, axis=1)
            if df.shape[0]==0:
                continue   
            print(pic_flag)
            print(df['Tactic'].iloc[0])
            print(ranking.set_index(df['Opponent']).transpose())  
        
            #now, plot the top several options
            coln=0
            for col in ranking:
                if ranking.shape[1]<2:
                    
                    plt.plot(ranking[col],linewidth=0.5,marker='*',label=col)
                else:
                    plt.plot(ranking[col]-ranking[ranking.columns[0]],linewidth=0.5,marker = 'o',label=col)
                plt.title('vs '+df['Tactic'].mode().iloc[0]+' pic recent, best='+ranking.columns[0])
                plt.xticks(ticks=df['Opponent'].index, labels=df['Opponent'].values,\
                           fontsize=7,rotation = 90)
                coln=coln+1
                if coln>plot_best:
                    break
            plt.legend()
            plt.show()       
                  

  
        
        
    results_present(res_pic,res_pin,ratings_array,test_ratings_labels,\
                        test_individual_orders,\
                        matches_since_season_start=matches_since_season_start\
                            ,plot_best=5)
    results_array_prune(filename='full_ra_withres.csv',filename1=str(nt_id)+'_test_individual.csv',filename2=str(nt_id)+'_test_ratings.csv',filename3=str(nt_id)+'_test_specs.csv')

    """
    print('with pic - red')
    result_examine(res_pic[2],ratings_array,test_ratings_labels,averages_only=True)
    print('with pic - larry')
    #result_examine(res_pic[5],ratings_array,test_ratings_labels,averages_only=True)    
    
    print('with pin - red')
    result_examine(res_pin[2],ratings_array,test_ratings_labels,averages_only=True)
    print('with pin - larry')
    #result_examine(res_pin[5],ratings_array,test_ratings_labels,averages_only=True)                
    """    
     
    def historic_ratings_simulate():    
        print('simulating historic matches for opposing NT')    
        #To test the siulation of goals in the matches in the full history against the 
        #expected goals in the HT matches
        wins_array,draws_array,losses_array,\
            wins_array2,draws_array2,losses_array2,\
            goals_historic_home,goals_historic_away,\
            goals_predicted_home,goals_predicted_away=\
                ratings_array_rearrange(ratings_array,\
                                test_ratings=pd.DataFrame(),\
                                    predict_with_spex=True,\
                                    test_specs=None,\
                                        scale=0,\
                                        historic_match_simulation=True)
            
            
        ratings_array['Average_goals_predicted']=goals_predicted_home
        ratings_array['Average_goals_predicted_']=goals_predicted_away
        
        print(ratings_array[['Tactic','Average_goals_predicted','Average goals']])
        print(ratings_array[['Tactic_','Average_goals_predicted_','Average goals_']])                        
        
   

        




   
   

