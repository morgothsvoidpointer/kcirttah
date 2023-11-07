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

filename='htme_sim.xlsx'
excel=ExcelCompiler(os.getcwd()+'/'+filename)

excel.evaluate('simulator!P2')
excel.evaluate('simulator!Q2')
excel.evaluate('simulator!R2')

spex=excel.evaluate('simulator!J4')

excel.set_value('simulator!J4','Yes')

print(spex)

#excel_backup=ExcelCompiler(os.getcwd()+'/'+filename)

from string import ascii_uppercase


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
                 formation_away\
                 ):

    home_cells=['D14','E14','F14','E15','D16','E16','F16']
    away_cells=['D18','E18','F18','E19','D20','E20','F20']
    for i in range(len(ratings_home)):
        excel.set_value('simulator!'+home_cells[i],ratings_home[i])
    for i in range(len(ratings_away)):
        excel.set_value('simulator!'+away_cells[i],ratings_away[i])        
    
        
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

    
    
    
    W=excel.evaluate('simulator!P2')
    D=excel.evaluate('simulator!Q2')
    L=excel.evaluate('simulator!R2')
    return W,D,L,excel


if __name__=='__main__':
    W,D,L,excel=wdl_nicarana(ratings_home,\
                     ratings_away,\
                     metaratings_home,\
                     metaratings_away,\
                     formation_home,\
                     formation_away\
                     )



    print(W)
    print(D)
    print(L)
