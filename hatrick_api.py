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
    home_data['ISP defense']=home_ratings.indirect_set_pieces_defense/4+0.75
    home_data['Tactic']=tactic_id_dict[match.home_team.tactic_type]
    home_data['Tactic skill']=match.home_team.tactic_skill
    home_data['Style of play']=match.home_team.team_attitude
    home_data['Total exp']=0
    home_data['Average goals']=0
    home_formation=match.home_team.formation
    home_data['Formation']=home_formation
    home_data['Defender_number']=home_formation.split('-')[0]
    home_data['Mid_number']=home_formation.split('-')[1]
    home_data['Forward_number']=home_formation.split('-')[2]
    home_data['Actual goals']=match.home_team.goals
    
    #extract the player specs map and form map
    
    
    
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
    away_data['ISP defense']=away_ratings.indirect_set_pieces_defense/4+0.75
    away_data['Tactic']=tactic_id_dict[match.away_team.tactic_type]
    away_data['Tactic skill']=match.away_team.tactic_skill
    away_data['Style of play']=match.away_team.team_attitude
    away_data['Total exp']=0
    away_data['Average goals']=0
    away_formation=match.away_team.formation
    away_data['Formation']=away_formation
    away_data['Defender_number']=away_formation.split('-')[0]
    away_data['Mid_number']=away_formation.split('-')[1]
    away_data['Forward_number']=away_formation.split('-')[2]
    away_data['Actual goals']=match.away_team.goals
    
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
    from hattrick_auth import *
    access_token=ht_auth()
    chpp=chpp_object_create(access_token)
    match_id=36816805
    match = chpp.match(match_id,source_system='HTOIntegrated')
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
    home_data['ISP defense']=home_ratings.indirect_set_pieces_defense/4+0.75
    home_data['Tactic']=tactic_id_dict[match.home_team.tactic_type]
    home_data['Tactic skill']=match.home_team.tactic_skill
    home_data['Style of play']=match.home_team.team_attitude
    home_data['Total exp']=0
    home_data['Average goals']=0
    home_formation=match.home_team.formation
    home_data['Formation']=home_formation
    home_data['Defender_number']=home_formation.split('-')[0]
    home_data['Mid_number']=home_formation.split('-')[1]
    home_data['Forward_number']=home_formation.split('-')[2]
    home_data['Actual goals']=match.home_team.goals
    
    
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
    away_data['ISP defense']=away_ratings.indirect_set_pieces_defense/4+0.75
    away_data['Tactic']=tactic_id_dict[match.away_team.tactic_type]
    away_data['Tactic skill']=match.away_team.tactic_skill
    away_data['Style of play']=match.away_team.team_attitude
    away_data['Total exp']=0
    away_data['Average goals']=0
    away_formation=match.away_team.formation
    away_data['Formation']=away_formation
    away_data['Defender_number']=away_formation.split('-')[0]
    away_data['Mid_number']=away_formation.split('-')[1]
    away_data['Forward_number']=away_formation.split('-')[2]
    away_data['Actual goals']=match.away_team.goals    
    
    
    
    
