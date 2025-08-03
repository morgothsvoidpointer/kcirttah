# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 12:34:07 2025

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

from ht_ratings_export import nt_id,nt_id_mine


    #%% PREDICTOR


def tactic_extract(arr,t='Normal',limit=np.inf):
    """
    Extracts rows corresponding to a tactic

    Parameters
    ----------
    arr : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    return arr[arr['Tactic']==t].iloc[:limit]

def str_merge(s1,s2):
    if len(s1)!=len(s2):
        return None
    s=[]
    for i in range(len(s1)):
       s.append(s1[i]+s2[i])
    return s

scale_pic_pin={}
scale_pic_pin[1]='pin'
scale_pic_pin[2]='pic'




def quick_dirty_compare(nt_id,nt_id_mine,limit=10,display_formation=False):
    """
    

    Parameters
    ----------
    nt_id : TYPE
        DESCRIPTION.
    nt_id_mine : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """    
    #%%
    from nickarana_ht_sim_fromexcel import ratings_array_rearrange
    
    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    arr2=pd.read_csv(str(nt_id_mine)+'_ratings_data.csv')
    
    arr1=arr1[arr1['Competition']!='Friendly']
    arr2=arr2[arr2['Competition']!='Friendly']
    limit=50
    for scale in range(2):
        for scale2 in range(2):
            
            
            wins_array,draws_array,losses_array,\
            wins_array2,draws_array2,losses_array2=\
            ratings_array_rearrange(arr1,\
                                    arr2,\
                                    predict_with_spex=True,\
                                    test_specs_array=None,\
                                    scale=scale+1,\
                                    historic_match_simulation=True,\
                                    scale2=scale2+1,\
                                    limit=limit)
            print('them '+str(scale_pic_pin[scale+1]))
            print('us '+str(scale_pic_pin[scale2+1]))
            print(wins_array)
            
            if limit==np.inf:
                limit_=1000000000000000
            else:
                limit_=limit
                
            #now, need to present appropriately
            #add indices back in
            wins_pd=pd.DataFrame(wins_array)
            wins_pd.columns=arr1.index[:limit_]
            wins_pd.index=arr2.index[:limit_]
            
            
            #split into different tactics as played by each side:
                
            #N vs N    
                
            tac_limit=10
            tactics_consider=['Normal','Counter-attacks']
            rows_bytac1={}
            rows_bytac2={}
            for tac in tactics_consider:
                rows_bytac1[tac]=tactic_extract(arr1,tac,tac_limit)
                rows_bytac2[tac]=tactic_extract(arr2,tac,tac_limit)
            
            #now for each combination, pull the WDL percentages:
            for tac1 in rows_bytac1.keys():
                for tac2 in rows_bytac2.keys():
                    rows1=rows_bytac1[tac1]
                    rows2=rows_bytac2[tac2]
                    inds1=rows1.index
                    inds2=rows2.index
                    tnames1=[tn[:3] for tn in rows1['Team name_']]
                    tnames1_ha=str_merge(tnames1,rows1['HomeOrAway'].values)
                    
                    tnames2=[tn[:3] for tn in rows2['Team name_']]
                    tnames2_ha=str_merge(tnames2,rows2['HomeOrAway'].values)
                    
                    print('them - '+tac1+', '+scale_pic_pin[scale+1])
                    print('us - '+tac2+', '+scale_pic_pin[scale2+1])
                    print('win chance')
                    wins_bytac=wins_pd[inds1].iloc[inds2]
                    wins_bytac.columns=tnames1_ha
                    wins_bytac.index=tnames2_ha

                        
                    #will we need to attach other info than country name?
                    #possibly the formation
                    display_formation=0
                    if display_formation:
                        pass
                        #need to extract individual orders from hattrick!
                        #also the ye olde question of subs etc
                    
                    #mean and variance
                    #calc row and column mean and variance
                    rowmean=wins_bytac.mean(axis=1)
                    colmean=wins_bytac.mean(axis=0)
                    rowstd=wins_bytac.std(axis=1)
                    colstd=wins_bytac.std(axis=0)
                    
                    overall_mean=np.mean(wins_bytac)
                    overall_std=np.std(wins_bytac)
                    
                    wins_bytac['mean']=rowmean
                    wins_bytac['std']=rowstd
                    wins_bytac=pd.concat([wins_bytac,pd.concat([colmean,colstd],axis=1).rename({0:'mean',1:'std'},axis=1).transpose()],axis=0)

                    wins_bytac['mean'].loc['mean']=overall_mean
                    wins_bytac['std'].loc['std']=overall_std

                    print(wins_bytac)                    
            
#%%

def finer_categorisation_tactics(nt_id):
    """
    

    Parameters
    ----------
    nt_id : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """    
    
    
    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')

    #which tactics to isolate?
    
    #343
    #all attacking - by attitude?
    # AoA - att/def ratio
    #CA 442 vs hard CA
    #defensive - att/def ratio
    
    
if __name__=='__main__':
    quick_dirty_compare(nt_id,nt_id_mine,limit=10)
  