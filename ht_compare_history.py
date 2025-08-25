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
from py_markdown_table.markdown_table import markdown_table

from github_upload import github_upload
from ht_ratings_export import nt_id,nt_id_mine
from ht_finer_categorisation import finer_categorisation_tactics
from orders_spex import osx_array
from nickarana_ht_sim_fromexcel import ratings_array_rearrange

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

def style_extract(arr,t='bal',limit=np.inf):
    
    
    
    return arr[arr['T_C']==t].iloc[:limit]


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


wldict={}
wldict[0]='W'
wldict[1]='L'



def quick_tactics_compare(nt_id,nt_id_mine,tactics_consider=['Normal','Counter-attacks'],limit=10,display_formation=False,load_from_file=True):
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

    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    arr2=pd.read_csv(str(nt_id_mine)+'_ratings_data.csv')
    osx_array(str(nt_id))
    osx_array(str(nt_id_mine))
    arr1=arr1[arr1['Competition']!='Friendly']
    arr2=arr2[arr2['Competition']!='Friendly']
    limit=50
    file_name0='win_'+str(nt_id_mine)+'_vs_'+str(nt_id)+'.md'
    f0=open(file_name0,mode='w', encoding="utf-8")
    file_name1='loss_'+str(nt_id_mine)+'_vs_'+str(nt_id)+'.md'
    f1=open(file_name1,mode='w', encoding="utf-8")
    f=[f0,f1]
    data_dict={}
    data_dict['pin']={}
    data_dict['pic']={}    
    data_dict['pin']['pin']={}
    data_dict['pin']['pic']={}
    data_dict['pic']['pin']={}
    data_dict['pic']['pic']={}
    data_dict['pin']['pin']['W']={}
    data_dict['pin']['pic']['W']={}
    data_dict['pic']['pin']['W']={}
    data_dict['pic']['pic']['W']={}
    data_dict['pin']['pin']['L']={}
    data_dict['pin']['pic']['L']={}
    data_dict['pic']['pin']['L']={}
    data_dict['pic']['pic']['L']={}
    
    
    
    for scale in range(2):
        for scale2 in range(2):
            
            
            wins_ss=str(nt_id_mine)+'_'+str(nt_id)+'wins'+str(scale)+str(scale2)+'.csv'
            losses_ss=str(nt_id_mine)+'_'+str(nt_id)+'lossess'+str(scale)+str(scale2)+'.csv'

            if load_from_file:
                wins_array=np.genfromtxt(wins_ss)
                losses_array=np.genfromtxt(losses_ss)
            else:
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
                print('Cols '+str(nt_id)+', '+str(scale_pic_pin[scale+1]))
                print('Rows '+str(nt_id_mine)+', '+str(scale_pic_pin[scale2+1])) 
                np.savetxt(wins_ss,wins_array)
                np.savetxt(losses_ss,losses_array)
            
            
            if limit==np.inf:
                limit_=1000000000000000
            else:
                limit_=limit
                
            #now, need to present appropriately
            #add indices back in
            wins_pd=pd.DataFrame(wins_array)
            wins_pd.columns=arr1.index[:limit_]
            wins_pd.index=arr2.index[:limit_]
            
            losses_pd=pd.DataFrame(losses_array)
            losses_pd.columns=arr1.index[:limit_]
            losses_pd.index=arr2.index[:limit_]            
     
            for en,D in enumerate([wins_pd,losses_pd]):
                
                #split into different tactics as played by each side:
                    
                #N vs N    
                    
                tac_limit=10
                
                rows_bytac1={}
                rows_bytac2={}
                for tac in tactics_consider:
                    rows_bytac1[tac]=tactic_extract(arr1,tac,tac_limit)
                    rows_bytac2[tac]=tactic_extract(arr2,tac,tac_limit)
                
                
                
                
                #now for each combination, pull the WDL percentages:
                for tac1 in rows_bytac1.keys():
                    data_dict[scale_pic_pin[scale+1]][scale_pic_pin[scale2+1]][wldict[en]][tac1]={}
                    for tac2 in rows_bytac2.keys():
                        rows1=rows_bytac1[tac1]
                        rows2=rows_bytac2[tac2]
                        if rows1.shape[0]==0 or rows2.shape[0]==0:
                            continue
                        inds1=rows1.index
                        inds2=rows2.index
                        tnames1=[tn[:3] for tn in rows1['Team name_']]
                        tnames1_ha=str_merge(tnames1,rows1['HomeOrAway'].values)
                        
                        tnames2=[tn[:3] for tn in rows2['Team name_']]
                        tnames2_ha=str_merge(tnames2,rows2['HomeOrAway'].values)
                        str0='Cols - '+str(nt_id)+', '+tac1+', '+scale_pic_pin[scale+1]
                        print(str0)
                        f[en].write('* '+str0+'\n')
                        str1='Rows - '+str(nt_id_mine)+', '+tac2+', '+scale_pic_pin[scale2+1]
                        print(str1)
                        f[en].write('* '+str1+'\n')
                        
                        if en:
                            print('loss chance')
                            #f[en].write('loss chance')
                        else:
                            print('win chance')
                            #f[en].write('win chance')
                            
                            
                        D_bytac=D[inds1].loc[inds2]
                        D_bytac.columns=tnames1_ha
                        D_bytac.index=tnames2_ha
    
                            
                        #will we need to attach other info than country name?

                        #mean and variance
                        #calc row and column mean and variance
                        rowmean=D_bytac.mean(axis=1)
                        colmean=D_bytac.mean(axis=0)
                        rowstd=D_bytac.std(axis=1)
                        colstd=D_bytac.std(axis=0)
                        
                        overall_mean=np.mean(D_bytac)
                        overall_std=np.std(D_bytac.values)
                        
                        D_bytac['mean']=rowmean
                        D_bytac['std']=rowstd
                        D_bytac=pd.concat([D_bytac,pd.concat([colmean,colstd],axis=1).rename({0:'mean',1:'std'},axis=1).transpose()],axis=0)
    
                        D_bytac.at['mean','mean']=overall_mean
                        D_bytac.at['std','std']=overall_std
                        
                        #now add the formational/orders info
                        
                        display_formation=1
                        if display_formation:
                            formation1=arr1['Indiv Order'].loc[inds1]
                            formation2=arr2['Indiv Order'].loc[inds2]
                            
                            def1=[f1[1:6] for f1 in formation1]+[None]*2
                            mid1=[f1[6:11] for f1 in formation1]+[None]*2
                            att1=[' '+f1[11:14]+' ' for f1 in formation1]+[None]*2
                            
                            def2=[f2[1:6] for f2 in formation2]+[None]*5
                            mid2=[f2[6:11] for f2 in formation2]+[None]*5
                            att2=[f2[11:14] for f2 in formation2]+[None]*5
                            
                            D_bytac['defence']=def1
                            D_bytac['midfield']=mid1
                            D_bytac['attack']=att1
                            
                            def2_ser=pd.Series(def2,index=D_bytac.columns)
                            mid2_ser=pd.Series(mid2,index=D_bytac.columns)
                            att2_ser=pd.Series(att2,index=D_bytac.columns)
                            
                            D_bytac=pd.concat([D_bytac,pd.concat([def2_ser,mid2_ser,att2_ser],axis=1).rename({0:'defence',1:'midfield',2:'attack'},axis=1).transpose()],axis=0)
 
                            print(D_bytac)
                            
                            

                            #also the ye olde question of subs etc
                                                
                        
                        
                        #markdown = markdown_table(D_bytac).get_markdown()
                        md_string=D_bytac.to_markdown()
                        f[en].write('\n')
                        f[en].write(md_string)
                        f[en].write('\n')
                        f[en].write('\n')
                        print(D_bytac)
                        data_dict[scale_pic_pin[scale+1]][scale_pic_pin[scale2+1]][wldict[en]][tac1][tac2]=D_bytac

                        
    f0.close()
    f1.close()
    
    try:  
        github_upload(file_name0)
        github_upload(file_name1)
    except:
        print('not connected to github maybe')
    return data_dict
#%%

def custom_tactics_compare(nt_id,nt_id_mine,tactics_consider=['bal','442ca','343'],limit=10,display_formation=False,load_from_file=True):
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
    
    finer_categorisation_tactics(str(nt_id))
    finer_categorisation_tactics(str(nt_id_mine))    
    osx_array(str(nt_id))
    osx_array(str(nt_id_mine))
    
    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    arr2=pd.read_csv(str(nt_id_mine)+'_ratings_data.csv')
    
    
    
    
    arr1=arr1[arr1['Competition']!='Friendly']
    arr2=arr2[arr2['Competition']!='Friendly']
    limit=50
    file_name0='win0_'+str(nt_id_mine)+'_vs_'+str(nt_id)+'.md'
    f0=open(file_name0,mode='w', encoding="utf-8")
    file_name1='loss0 _'+str(nt_id_mine)+'_vs_'+str(nt_id)+'.md'
    f1=open(file_name1,mode='w', encoding="utf-8")
    f=[f0,f1]
    data_dict={}
    data_dict['pin']={}
    data_dict['pic']={}    
    data_dict['pin']['pin']={}
    data_dict['pin']['pic']={}
    data_dict['pic']['pin']={}
    data_dict['pic']['pic']={}
    data_dict['pin']['pin']['W']={}
    data_dict['pin']['pic']['W']={}
    data_dict['pic']['pin']['W']={}
    data_dict['pic']['pic']['W']={}
    data_dict['pin']['pin']['L']={}
    data_dict['pin']['pic']['L']={}
    data_dict['pic']['pin']['L']={}
    data_dict['pic']['pic']['L']={}
        
    
    for scale in range(2):

        for scale2 in range(2):
            
            
            wins_ss=str(nt_id_mine)+'_'+str(nt_id)+'wins'+str(scale)+str(scale2)+'.csv'
            losses_ss=str(nt_id_mine)+'_'+str(nt_id)+'lossess'+str(scale)+str(scale2)+'.csv'
            
            if load_from_file:
                wins_array=np.genfromtxt(wins_ss)
                losses_array=np.genfromtxt(losses_ss)
            else:
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
                print('Cols '+str(nt_id)+', '+str(scale_pic_pin[scale+1]))
                print('Rows '+str(nt_id_mine)+', '+str(scale_pic_pin[scale2+1])) 
                np.savetxt(wins_ss,wins_array)
                np.savetxt(losses_ss,losses_array)
                        

            if limit==np.inf:
                limit_=1000000000000000
            else:
                limit_=limit
                
            #now, need to present appropriately
            #add indices back in
            wins_pd=pd.DataFrame(wins_array)
            wins_pd.columns=arr1.index[:limit_]
            wins_pd.index=arr2.index[:limit_]
            
            losses_pd=pd.DataFrame(losses_array)
            losses_pd.columns=arr1.index[:limit_]
            losses_pd.index=arr2.index[:limit_]            
     
            for en,D in enumerate([wins_pd,losses_pd]):
                
                #split into different tactics as played by each side:
                    
                #N vs N    
                    
                tac_limit=10
                
                rows_bytac1={}
                rows_bytac2={}
                for tac in tactics_consider:
                    rows_bytac1[tac]=style_extract(arr1.iloc[:limit_],tac,tac_limit)
                    rows_bytac2[tac]=style_extract(arr2.iloc[:limit_],tac,tac_limit)
                
                
            
                #now for each combination, pull the WDL percentages:
                for tac1 in rows_bytac1.keys():
                    data_dict[scale_pic_pin[scale+1]][scale_pic_pin[scale2+1]][wldict[en]][tac1]={}
                    for tac2 in rows_bytac2.keys():
                        rows1=rows_bytac1[tac1]
                        rows2=rows_bytac2[tac2]
                        if rows1.shape[0]==0 or rows2.shape[0]==0:
                            continue
                        inds1=rows1.index
                        inds2=rows2.index
                        tnames1=[tn[:3] for tn in rows1['Team name_']]
                        tnames1_ha=str_merge(tnames1,rows1['HomeOrAway'].values)
                        
                        tnames2=[tn[:3] for tn in rows2['Team name_']]
                        tnames2_ha=str_merge(tnames2,rows2['HomeOrAway'].values)
                        str0='Cols - '+str(nt_id)+', '+tac1+', '+scale_pic_pin[scale+1]
                        print(str0)
                        f[en].write('* '+str0+'\n')
                        str1='Rows - '+str(nt_id_mine)+', '+tac2+', '+scale_pic_pin[scale2+1]
                        print(str1)
                        f[en].write('* '+str1+'\n')
                        
                        if en:
                            print('loss chance')
                            #f[en].write('loss chance')
                        else:
                            print('win chance')
                            #f[en].write('win chance')
                            
                            
                        D_bytac=D[inds1].loc[inds2]
                        D_bytac.columns=tnames1_ha
                        D_bytac.index=tnames2_ha
    
                            
                        #will we need to attach other info than country name?

                        #mean and variance
                        #calc row and column mean and variance
                        rowmean=D_bytac.mean(axis=1)
                        colmean=D_bytac.mean(axis=0)
                        rowstd=D_bytac.std(axis=1)
                        colstd=D_bytac.std(axis=0)
                        
                        overall_mean=np.mean(D_bytac)
                        overall_std=np.std(D_bytac.values)
                        
                        D_bytac['mean']=rowmean
                        D_bytac['std']=rowstd
                        D_bytac=pd.concat([D_bytac,pd.concat([colmean,colstd],axis=1).rename({0:'mean',1:'std'},axis=1).transpose()],axis=0)
    
                        D_bytac.at['mean','mean']=overall_mean
                        D_bytac.at['std','std']=overall_std
                        
                        
                         
                        
                        #now add the formational/orders info
                        
                        display_formation=1
                        if display_formation:
                            formation1=arr2['Indiv Order'].loc[inds2]
                            formation2=arr1['Indiv Order'].loc[inds1]
                            
                            def1=[f1[1:6] for f1 in formation1]+[None]*2
                            mid1=[f1[6:11] for f1 in formation1]+[None]*2
                            att1=[' '+f1[11:14]+' ' for f1 in formation1]+[None]*2
                            
                            def2=[f2[1:6] for f2 in formation2]+[None]*5
                            mid2=[f2[6:11] for f2 in formation2]+[None]*5
                            att2=[f2[11:14] for f2 in formation2]+[None]*5
                            
                            D_bytac['defence']=def1
                            D_bytac['midfield']=mid1
                            D_bytac['attack']=att1
                            
                            def2_ser=pd.Series(def2,index=D_bytac.columns)
                            mid2_ser=pd.Series(mid2,index=D_bytac.columns)
                            att2_ser=pd.Series(att2,index=D_bytac.columns)
                            
                            D_bytac=pd.concat([D_bytac,pd.concat([def2_ser,mid2_ser,att2_ser],axis=1).rename({0:'defence',1:'midfield',2:'attack'},axis=1).transpose()],axis=0)
                            D_bytac = D_bytac.replace(np.nan, None)
                            print(D_bytac)
                            
                            

                            #also the ye olde question of subs etc
                                                
                        
                        
                        #markdown = markdown_table(D_bytac).get_markdown()
                        md_string=D_bytac.to_markdown()
                        f[en].write('\n')
                        f[en].write(md_string)
                        f[en].write('\n')
                        f[en].write('\n')
                        print(D_bytac)   
                        data_dict[scale_pic_pin[scale+1]][scale_pic_pin[scale2+1]][wldict[en]][tac1][tac2]=D_bytac
    f0.close()
    f1.close()
    try:  
        github_upload(file_name0)
        github_upload(file_name1)
    except:
        print('not connected to github maybe')
        
#%%
    return data_dict
    
if __name__=='__main__':
    
    load_from_file=True
    
    dd1=quick_tactics_compare(nt_id,nt_id_mine,tactics_consider=['Normal','Counter-attacks'],limit=10,load_from_file=load_from_file)
    
    dd2=custom_tactics_compare(nt_id,nt_id_mine,tactics_consider=['bal','442ca','343'],limit=10,load_from_file=load_from_file)

    #now create arrays of means
    
    
    
    
    
    


