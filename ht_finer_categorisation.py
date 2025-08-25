# -*- coding: utf-8 -*-
"""
 Created on Sun Aug  3 23:07:36 2025

@author: Tyufik
"""
import pandas as pd

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
    #%%
    
    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    arr1.drop('Unnamed: 0', axis=1, inplace=True)
    tlabel=[]
    #which tactics to isolate?
    
    
    
    #current tactics:
    #Normal/AIM/AOW
    #CA
    #LS
    #Press
    #PC
    
    #could merge AIM, AOW, PC into others?
    
    #new tactics:

    
    #Normal/AIM/AOW
    #343
    #other attacking - by attitude?
    # AoA - att/def ratio
    #All ther others
    #Defensive - 451/541 + Press
    
    #CA
    #CA 442 vs hard CA - hard CA is all 532, all 541 and most 442 'with arrows'. 
    #defensive - att/def ratio
    

    
    
    #343
    #label '343'
    for i in range(arr1.shape[0]):
        row=arr1.iloc[i]

        #isolate tactics columns
        tactic=row['Tactic']
        
        #isolate formation column
        formation=row['Formation']
        
        def_ratings=row[["Right defence","Central defence","Left defence"]].tolist()
        
        #import att/def
        attdef=row['Style of play']/10  
        
        
        if tactic in ['Normal','Attack in the middle','Attack on wings','Pressing','Play creatively']:
            if formation=='3-4-3':
                tlabel.append('343')
            elif attdef>0.75:
                #if 2 defenses are level 13, then this is not AoA
                def_ratings.sort(reverse=True)
                if def_ratings[0]>=13 and def_ratings[1]>=13:
                    tlabel.append('AoA')
                else:
                    tlabel.append('att')
            elif (attdef<-0.5 or tactic=='Pressing') and tactic!='Play creatively':
                tlabel.append('AoD')
            elif tactic=='Play creatively':
                tlabel.append('PC')
            else:
                tlabel.append('bal')
        elif tactic=='Long shots':
            tlabel.append('LS')
        elif tactic=='Counter-attacks':
            if formation=='5-4-1' or formation=='5-3-2' or formation=='5-2-3' or formation=='4-3-3':
                tlabel.append('hardca')
            elif formation=='4-4-2':
                tlabel.append('442ca')
            else:
                tlabel.append('otherca')
            #TODO: hard 442 ca    
    arr1['T_C']=tlabel            
    print(tlabel)
    arr1.to_csv(str(nt_id)+'_ratings_data.csv')        
    
    return arr1

    #%%
if __name__=='__main__':
    results_arr=finer_categorisation_tactics(3011)
    
    
    
    