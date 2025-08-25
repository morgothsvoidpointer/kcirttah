# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 14:24:24 2025

@author: Tyufik
"""

import pandas as pd

io_dict={}
io_dict['0']='N'
io_dict['1']='O'
io_dict['2']='D'
io_dict['3']='M'
io_dict['4']='W'




def orders_spex(O,S):
    O=str(O).zfill(11)
    opos=0
    N=[]
    for n,s in enumerate(S):
        if s=='E':
            N.append('-')
            continue
        o=O[opos]
        N.append(io_dict[o])
        opos=opos+1
    return ''.join(N)

def osx_array(nt_id):
    arr1=pd.read_csv(str(nt_id)+'_ratings_data.csv')
    arr1.drop('Unnamed: 0', axis=1, inplace=True)
    
    Narr=arr1[['Orders','spex']].apply(lambda x: orders_spex(x.Orders, x.spex), axis=1)
    arr1['Indiv Order']=Narr
    arr1.to_csv(str(nt_id)+'_ratings_data.csv')