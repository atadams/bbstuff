import os
import time
import urllib.request as request
import json
from datetime import datetime
from pathlib import Path

import requests

from config.settings.base import APPS_DIR, MEDIA_ROOT, PLAY_VIDEO_ROOT
from game.models import Pitch, Player
from game.utils import get_ab, get_game, get_pitch, get_player_by_id_name, get_team_by_dict

pitches = Pitch.objects.filter(data__pitch_type='FF')

interval = 5
times = 1

headers = {'referer': 'https://www.mlb.com/video/', }

game_id = 631393
feeds = ['team_home', 'team_away']
save_path = './media/'
# save_path = '/Users/aadams/Downloads/astro_video/'

# home, away, network
clips_base_url = f'https://fastball-clips.mlb.com/{game_id}/home'

i = 0

while i != times:

    print('\n=============\n')

    with request.urlopen(f'https://baseballsavant.mlb.com/gf?game_pk={game_id}&_=159621768973{i}') as response:
        source = response.read()
        data = json.loads(source)

        home_team = get_team_by_dict(data['home_team_data'])
        away_team = get_team_by_dict(data['away_team_data'])
        game_date = datetime.strptime(data['game_date'], '%Y-%m-%d')

        game = get_game(data['scoreboard']['gamePk'], game_date, data['game_status'], home_team, away_team, data)
        path_name = f'{PLAY_VIDEO_ROOT}{game.path_name_with_id}'
        Path(path_name).mkdir(parents=True, exist_ok=True)

        for feed in feeds:
            top_bottom = 't' if feed == 'team_home' else 'b'
            top_bottom_full = 'Top' if feed == 'team_home' else 'Bottom'

            for play in data[feed]:
                print(play['rowId'], play['batter'], play['pitcher'])
                batter = get_player_by_id_name(play['batter'], play['batter_name'])
                pitcher = get_player_by_id_name(play['pitcher'], play['pitcher_name'])
                at_bat = get_ab(game, play, top_bottom_full)

                pitch = get_pitch(at_bat, play)
                print(pitch.data['game_total_pitches'])

                current_id = pitch.data['game_total_pitches']

                next_id = pitch.next_pitch_id

                if not os.path.exists(pitch.video_filepath):
                    file_url = f'{clips_base_url}/{play["play_id"]}.mp4'

                    myfile = requests.get(file_url, headers=headers)

                    if myfile.ok:
                        open(pitch.video_filepath, 'wb').write(myfile.content)
                        print(f'{game_id}: Success: ({feed}): {pitch.video_filename()}')
                    else:
                        print(f'{game_id}: Failure ({feed}): {pitch.video_filename()}, {file_url}')

    # time.sleep(interval)
    i += 1
