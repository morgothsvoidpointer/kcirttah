from pychpp import CHPP
import pandas as pd    



tournament_dict={}
tournament_dict[5001279]='Asia and Oceania Cup'
tournament_dict[5001315]='World Cup'
tournament_dict[5001278]='Africa Cup'
tournament_dict[5001277]='America Cup'
tournament_dict[5001273]='Europe Cup'
tournament_dict[5001319]='Nations Cup'
tournament_dict[5001311]='Wildcard'
tournament_dict[6244933]='Contender League'
tournament_dict[0]='Friendly'

tactic_id_dict={}
tactic_id_dict[0]='Normal'
tactic_id_dict[1]='Pressing'
tactic_id_dict[2]='Counter-attacks'
tactic_id_dict[3]='Attack in the middle'
tactic_id_dict[4]='Attack in wings'
tactic_id_dict[7]='Play creatively'
tactic_id_dict[8]='Long shots'

spex_dict={}
spex_dict[0]='Z'
spex_dict[1]='T'
spex_dict[2]='Q'
spex_dict[3]='P'
spex_dict[4]='U'
spex_dict[5]='H'
spex_dict[6]='R'
spex_dict[8]='S'

iorder_dict={}
iorder_dict[0]='Normal'
iorder_dict[1]='Offensive'
iorder_dict[2]='Defensive'
iorder_dict[3]='Towards middle'
iorder_dict[4]='Towards wing'

player_dir={}

def get_match_data_chpp(chpp,match_id=36816805):
    match = chpp.match(match_id,source_system='HTOIntegrated')
    home_team_id=match.home_team.id
    away_team_id=match.away_team.id
    match_lineup_home=chpp.match_lineup(match_id,home_team_id,source_system='HTOIntegrated')
    match_lineup_away=chpp.match_lineup(match_id,away_team_id,source_system='HTOIntegrated')


    match_date=match.date
    
    
    match_data={}
    match_data['Match Datetime']=match_date.datetime
    match_data['campaign']=int(match_date.season/2)*2
    
    tournament_id=tournament_dict[match.context_id]
    match_data['Competition']=tournament_id
    
    home_data={}
    
    #home ratings
    home_ratings=match.home_team.ratings
    home_data['Team name']=match.home_team.name
    home_data['Midfield']=home_ratings.midfield/4+0.75
    home_data['Central attack']=home_ratings.mid_attack/4+0.75
    home_data['Central defence']=home_ratings.mid_defense/4+0.75
    home_data['Left attack']=home_ratings.left_attack/4+0.75
    home_data['Left defence']=home_ratings.left_defense/4+0.75
    home_data['Right attack']=home_ratings.right_attack/4+0.75
    home_data['Right defence']=home_ratings.right_defense/4+0.75
    home_data['ISP attack']=home_ratings.indirect_set_pieces_attack/4+0.75
    home_data['ISP defence']=home_ratings.indirect_set_pieces_defense/4+0.75
    home_data['Tactic']=tactic_id_dict[match.home_team.tactic_type]
    home_data['Tactic skill']=match.home_team.tactic_skill

    home_data['Average goals']=0
    home_formation=match.home_team.formation
    home_data['Formation']=home_formation
    home_data['Defender_number']=home_formation.split('-')[0]
    home_data['Mid_number']=home_formation.split('-')[1]
    home_data['Forward_number']=home_formation.split('-')[2]
    home_data['Actual goals']=match.home_team.goals
    
    #extract the player specs map and form map
    
    home_players=match_lineup_home.team_lineup.starting_lineup_players
    #update the player dictionary
    for p in home_players:
        player_id=p.id
        if player_id not in player_dir.keys():
            try:
                player_dir[player_id]=chpp.player(player_id)
            except:
                player_dir[player_id]=None
                print('error creating player object '+str(player_id))
        
    individual_orders_home=[h.behaviour for h in home_players]
    
    home_lineup=match_lineup_home.team_lineup.starting_lineup
    home_data['Style of play']=match_lineup_home.team_lineup.style_of_play
    home_data['Total exp']=match_lineup_home.team_lineup.experience_level
    
    home_spex=[]
    player_count=0
    did=home_lineup['KEEPER'][100].id
        
    playerobj=player_dir[did]
    if playerobj is not None:
        playerobj=chpp.player(did)
        home_spex.append(spex_dict[player_dir[did].specialty])
    else:
        home_spex.append('Z')  
    player_count=player_count+1
        
    defenders=[home_lineup['DEFENDER'][r] for r in range(101,106,1)]
    for d in defenders:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            home_spex.append(spex_dict[playerobj.specialty])
        else:
            home_spex.append('Z')
        player_count=player_count+1
    
    
    midfielders=[home_lineup['MIDFIELD'][r] for r in range(106,111,1)]
    for d in midfielders:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]
            
            if spec=='P':
                
                individual_order=individual_orders_home[player_count]
                if iorder_dict[individual_order]=='Defensive':
                    home_spex.append('p')
                else:
                    home_spex.append(spec)
            else:
                home_spex.append(spec)
        else:
            home_spex.append('Z')
        player_count=player_count+1
        



            
         

    forwards=[home_lineup['FORWARD'][r] for r in range(111,114,1)]
    for d in forwards:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]
            
            if spec=='P':
                
                individual_order=individual_orders_home[player_count]
                if iorder_dict[individual_order]!='Normal':
                    home_spex.append('p')
                else:
                    home_spex.append(spec)
            else:
                home_spex.append(spec)
        else:
            home_spex.append('Z')
        player_count=player_count+1
            
    home_data['spex']=''.join(home_spex)
    
    
    
    away_data={}
    
    #away ratings
    away_ratings=match.away_team.ratings
    away_data['Team name']=match.away_team.name
    away_data['Midfield']=away_ratings.midfield/4+0.75
    away_data['Central attack']=away_ratings.mid_attack/4+0.75
    away_data['Central defence']=away_ratings.mid_defense/4+0.75
    away_data['Left attack']=away_ratings.left_attack/4+0.75
    away_data['Left defence']=away_ratings.left_defense/4+0.75
    away_data['Right attack']=away_ratings.right_attack/4+0.75
    away_data['Right defence']=away_ratings.right_defense/4+0.75
    away_data['ISP attack']=away_ratings.indirect_set_pieces_attack/4+0.75
    away_data['ISP defence']=away_ratings.indirect_set_pieces_defense/4+0.75
    away_data['Tactic']=tactic_id_dict[match.away_team.tactic_type]
    away_data['Tactic skill']=match.away_team.tactic_skill


    away_data['Average goals']=0
    away_formation=match.away_team.formation
    away_data['Formation']=away_formation
    away_data['Defender_number']=away_formation.split('-')[0]
    away_data['Mid_number']=away_formation.split('-')[1]
    away_data['Forward_number']=away_formation.split('-')[2]
    away_data['Actual goals']=match.away_team.goals
    
    away_players=match_lineup_away.team_lineup.starting_lineup_players
    #update the player dictionary
    for p in away_players:
        player_id=p.id
        if player_id not in player_dir.keys():
            try:
                player_dir[player_id]=chpp.player(player_id)
            except:
                player_dir[player_id]=None
                print('error creating player object '+str(player_id))
    
    
    #extract the player specs map and form map
    away_lineup=match_lineup_away.team_lineup.starting_lineup
    away_data['Style of play']=match_lineup_away.team_lineup.style_of_play
    away_data['Total exp']=match_lineup_away.team_lineup.experience_level
    
    individual_orders_away=[h.behaviour for h in away_players]
    
    away_spex=[]
    player_count=0
    did=away_lineup['KEEPER'][100].id
        
    playerobj=player_dir[did]
    if playerobj is not None:
        playerobj=chpp.player(did)
        away_spex.append(spex_dict[player_dir[did].specialty])
    else:
        away_spex.append('Z')  
    player_count=player_count+1
        
    defenders=[away_lineup['DEFENDER'][r] for r in range(101,106,1)]
    for d in defenders:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            away_spex.append(spex_dict[playerobj.specialty])
        else:
            away_spex.append('Z')
        player_count=player_count+1
    
    
    midfielders=[away_lineup['MIDFIELD'][r] for r in range(106,111,1)]
    for d in midfielders:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]
            
            if spec=='P':
                
                individual_order=individual_orders_away[player_count]
                if iorder_dict[individual_order]=='Defensive':
                    away_spex.append('p')
                else:
                    away_spex.append(spec)
            else:
                away_spex.append(spec)
        else:
            away_spex.append('Z')
        player_count=player_count+1
        



            
         

    forwards=[away_lineup['FORWARD'][r] for r in range(111,114,1)]
    for d in forwards:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]
            
            if spec=='P':
                

                individual_order=individual_orders_away[player_count]
                if iorder_dict[individual_order]=='Normal':
                    away_spex.append('W')
                else:
                    away_spex.append(spec)
            else:
                away_spex.append(spec)
        else:
            away_spex.append('Z')
        player_count=player_count+1
            
    away_data['spex']=''.join(away_spex)
    
    
    
    
    
    return home_data,away_data,match_data

def get_match_list(chpp,team_id,seasons):
    march_together=[]

    for s in seasons:
        march=chpp.matches_archive(team_id,include_hto=True,season=s)
        march_together.extend(march.matches)
    dates=[]
    matchids=[]
    for m in march_together:
        matchid=m.id
        matchids.append(matchid)
        dte=m.date
        dates.append(dte.datetime)
    P=pd.DataFrame()
    P['m']=matchids
    P['d']=dates 
    P.sort_values(by='d',inplace=True,ascending=False)
    matchids_sorted=P['m'].tolist()
    return matchids_sorted

if __name__=='__main__':
    pass
#%%    
    from hattrick_auth import *
    access_token=ht_auth()
    chpp=chpp_object_create(access_token)
    match_id=36371020
    match = chpp.match(match_id,source_system='HTOIntegrated')
    home_team_id=match.home_team.id
    away_team_id=match.away_team.id
    match_lineup_home=chpp.match_lineup(match_id,home_team_id,source_system='HTOIntegrated')
    match_lineup_away=chpp.match_lineup(match_id,away_team_id,source_system='HTOIntegrated')


    match_date=match.date
    
    
    match_data={}
    match_data['Match Datetime']=match_date.datetime
    match_data['campaign']=int(match_date.season/2)*2
    
    tournament_id=tournament_dict[match.context_id]
    match_data['Competition']=tournament_id
    
    home_data={}
    
    #home ratings
    home_ratings=match.home_team.ratings
    home_data['Team name']=match.home_team.name
    home_data['Midfield']=home_ratings.midfield/4+0.75
    home_data['Central attack']=home_ratings.mid_attack/4+0.75
    home_data['Central defence']=home_ratings.mid_defense/4+0.75
    home_data['Left attack']=home_ratings.left_attack/4+0.75
    home_data['Left defence']=home_ratings.left_defense/4+0.75
    home_data['Right attack']=home_ratings.right_attack/4+0.75
    home_data['Right defence']=home_ratings.right_defense/4+0.75
    home_data['ISP attack']=home_ratings.indirect_set_pieces_attack/4+0.75
    home_data['ISP defence']=home_ratings.indirect_set_pieces_defense/4+0.75
    home_data['Tactic']=tactic_id_dict[match.home_team.tactic_type]
    home_data['Tactic skill']=match.home_team.tactic_skill

    home_data['Average goals']=0
    home_formation=match.home_team.formation
    home_data['Formation']=home_formation
    home_data['Defender_number']=home_formation.split('-')[0]
    home_data['Mid_number']=home_formation.split('-')[1]
    home_data['Forward_number']=home_formation.split('-')[2]
    home_data['Actual goals']=match.home_team.goals
    
    #extract the player specs map and form map
    
    home_players=match_lineup_home.team_lineup.starting_lineup_players
    #update the player dictionary
    for p in home_players:
        player_id=p.id
        if player_id not in player_dir.keys():
            try:
                player_dir[player_id]=chpp.player(player_id)
            except:
                player_dir[player_id]=None
                print('error creating player object '+str(player_id))
        
    individual_orders_home=[h.behaviour for h in home_players]
    
    home_lineup=match_lineup_home.team_lineup.starting_lineup
    home_data['Style of play']=match_lineup_home.team_lineup.style_of_play
    home_data['Total exp']=match_lineup_home.team_lineup.experience_level
    
    home_spex=[]
    player_count=0
    did=home_lineup['KEEPER'][100].id
        
    playerobj=player_dir[did]
    if playerobj is not None:
        playerobj=chpp.player(did)
        home_spex.append(spex_dict[player_dir[did].specialty])
    else:
        home_spex.append('Z')  
    player_count=player_count+1
        
    defenders=[home_lineup['DEFENDER'][r] for r in range(101,106,1)]
    for d in defenders:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            home_spex.append(spex_dict[playerobj.specialty])
        else:
            home_spex.append('Z')
        player_count=player_count+1
    
    
    midfielders=[home_lineup['MIDFIELD'][r] for r in range(106,111,1)]
    for d in midfielders:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]

            if spec=='P':
                

                individual_order=individual_orders_home[player_count]
                if iorder_dict[individual_order]=='Defensive':
                    home_spex.append('p')
                else:
                    home_spex.append(spec)
            else:
                home_spex.append(spec)
        else:
            home_spex.append('Z')
        player_count=player_count+1
        



            
         

    forwards=[home_lineup['FORWARD'][r] for r in range(111,114,1)]
    for d in forwards:
        if d is None:#if no player in this location
            home_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]
            
            if spec=='P':
                
                individual_order=individual_orders_home[player_count]
                if iorder_dict[individual_order]=='Normal':
                    home_spex.append('W')
                else:
                    home_spex.append(spec)
            else:
                home_spex.append(spec)
        else:
            home_spex.append('Z')
        player_count=player_count+1
            
    home_data['spex']=''.join(home_spex)
    
    
    
    away_data={}
    
    #away ratings
    away_ratings=match.away_team.ratings
    away_data['Team name']=match.away_team.name
    away_data['Midfield']=away_ratings.midfield/4+0.75
    away_data['Central attack']=away_ratings.mid_attack/4+0.75
    away_data['Central defence']=away_ratings.mid_defense/4+0.75
    away_data['Left attack']=away_ratings.left_attack/4+0.75
    away_data['Left defence']=away_ratings.left_defense/4+0.75
    away_data['Right attack']=away_ratings.right_attack/4+0.75
    away_data['Right defence']=away_ratings.right_defense/4+0.75
    away_data['ISP attack']=away_ratings.indirect_set_pieces_attack/4+0.75
    away_data['ISP defence']=away_ratings.indirect_set_pieces_defense/4+0.75
    away_data['Tactic']=tactic_id_dict[match.away_team.tactic_type]
    away_data['Tactic skill']=match.away_team.tactic_skill


    away_data['Average goals']=0
    away_formation=match.away_team.formation
    away_data['Formation']=away_formation
    away_data['Defender_number']=away_formation.split('-')[0]
    away_data['Mid_number']=away_formation.split('-')[1]
    away_data['Forward_number']=away_formation.split('-')[2]
    away_data['Actual goals']=match.away_team.goals
    
    away_players=match_lineup_away.team_lineup.starting_lineup_players
    #update the player dictionary
    for p in away_players:
        player_id=p.id
        if player_id not in player_dir.keys():
            try:
                player_dir[player_id]=chpp.player(player_id)
            except:
                player_dir[player_id]=None
                print('error creating player object '+str(player_id))
    
    
    #extract the player specs map and form map
    away_lineup=match_lineup_away.team_lineup.starting_lineup
    away_data['Style of play']=match_lineup_away.team_lineup.style_of_play
    away_data['Total exp']=match_lineup_away.team_lineup.experience_level
    
    individual_orders_away=[h.behaviour for h in away_players]
    
    away_spex=[]
    player_count=0
    did=away_lineup['KEEPER'][100].id
        
    playerobj=player_dir[did]
    if playerobj is not None:
        playerobj=chpp.player(did)
        away_spex.append(spex_dict[player_dir[did].specialty])
    else:
        away_spex.append('Z')  
    player_count=player_count+1
        
    defenders=[away_lineup['DEFENDER'][r] for r in range(101,106,1)]
    for d in defenders:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            away_spex.append(spex_dict[playerobj.specialty])
        else:
            away_spex.append('Z')
        player_count=player_count+1
    
    
    midfielders=[away_lineup['MIDFIELD'][r] for r in range(106,111,1)]
    for d in midfielders:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]

            if spec=='P':
                

                individual_order=individual_orders_away[player_count]
                if iorder_dict[individual_order]=='Defensive':
                    away_spex.append('p')
                else:
                    away_spex.append(spec)
            else:
                away_spex.append(spec)
        else:
            away_spex.append('Z')
        player_count=player_count+1
        



            
         

    forwards=[away_lineup['FORWARD'][r] for r in range(111,114,1)]
    for d in forwards:
        if d is None:#if no player in this location
            away_spex.append('E')
            continue
        did=d.id
        playerobj=player_dir[did]
        if playerobj is not None:
            spec=spex_dict[playerobj.specialty]

            if spec=='P':
                

                individual_order=individual_orders_away[player_count]
                if iorder_dict[individual_order]!='Normal':
                    away_spex.append('p')
                else:
                    away_spex.append(spec)
            else:
                away_spex.append(spec)
        else:
            away_spex.append('Z')
        player_count=player_count+1
            
    away_data['spex']=''.join(away_spex)
    
    
