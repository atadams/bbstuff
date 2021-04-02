import json
from urllib import request

import pandas as pd

PERCENT_FIELDS = [
    'ba',
    'est_ba',
    'bacon',
    'est_bacon',
    'babip',
    'obp',
    'slg',
    'est_obp',
    'est_slg',
    'iso',
    'est_iso',
    'fangraphs_woba',
    'fangraphs_est_woba',
    'fangraphs_wobacon',
    'fangraphs_est_wobacon',
]


def get_field_with_percentage(player_id, index_field='zone', data_field='ba', player_type='batter', year='2020',
                              p_throws='', pitch_type=''):
    dframe = pd.read_csv(
        get_statcast_url(player_id, player_type=player_type, year=year))

    if p_throws:
        dframe['p_throws'] = p_throws

    if pitch_type:
        dframe['pitch_type'] = pitch_type

    if data_field in PERCENT_FIELDS:
        numer = f'{data_field}_numer'
        denom = f'{data_field}_denom'

        zones = dframe.pivot_table(index=index_field, values=[f'{numer}', f'{denom}'], aggfunc='sum', fill_value=0)

        zones['ba'] = zones[numer] / zones[denom]

        return zones.round(3)
    else:
        return None


def get_statcast_url(player_id, player_type='batter', year='2020'):
    return f'https://baseballsavant.mlb.com/feed?evp=true&csv=true&hfGT=R%7C&hfSea={year}%7C&player_type={player_type}&{player_type}s_lookup[]={player_id}&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_pas=0&type=details&player_id={player_id}'


def get_player_stats(player_id):
    url = f'https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=currentTeam,team,stats(type=[yearByYear,yearByYearAdvanced,careerRegularSeason,careerAdvanced,availableStats](team(league)),leagueListId=mlb_hist)&site=en'

    with request.urlopen(url) as response:
        source = response.read()
        data = json.loads(source)

    return data['people'][0]



