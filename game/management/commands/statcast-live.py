import json
import os
import time
import urllib.request as request
from pathlib import Path

import requests
from dateutil.parser import parse
from django.core.management import BaseCommand

from config.settings.base import PLAY_VIDEO_ROOT
from game.utils import get_ab, get_game, get_pitch, get_team_by_dict


class Command(BaseCommand):
    def handle(self, *args, **options):
        interval = 2
        times = -1
        game_id = 634640
        download_videos = True
        save_highlights = False

        headers = {'referer': 'https://www.mlb.com/video/', }

        feeds = ['team_away', 'team_home']

        # home, away, network
        clips_base_url = f'https://fastball-clips.mlb.com/{game_id}/'

        i = 0

        print('game_id: ', game_id)

        while i != times:

            print('=============')
            # print(f'https://baseballsavant.mlb.com/gf?game_pk={game_id}&_=159621768973{i}')

            with request.urlopen(f'https://baseballsavant.mlb.com/gf?game_pk={game_id}&_=15962176{i}') as response:
                source = response.read()
                data = json.loads(source)
                # with open('/Users/aadams/Downloads/data3.json', 'w') as outfile:
                #     json.dump(data, outfile)

                if data['game_status'] == 'F':
                    times = i + 1

                if 'home_team_data' in data:
                    home_team = get_team_by_dict(data['home_team_data'])
                    away_team = get_team_by_dict(data['away_team_data'])
                else:
                    home_team = get_team_by_dict(data['scoreboard']['teams']['home'])
                    away_team = get_team_by_dict(data['scoreboard']['teams']['away'])

                if 'game_date' in data:
                    game_date = parse(data['game_date'])
                elif 'gameDate' in data:
                    game_date = parse(data['gameDate'])

                game = get_game(data['scoreboard']['gamePk'], game_date, data['game_status'], home_team, away_team,
                                data)

                path_name = f'{PLAY_VIDEO_ROOT}{game.path_name_with_id}'
                Path(path_name).mkdir(parents=True, exist_ok=True)

                with open(f'{path_name}/{game_id}.json', 'w') as outfile:
                    json.dump(data, outfile, indent=2)

                for feed in feeds:
                    top_bottom = 't' if feed == 'team_home' else 'b'
                    top_bottom_full = 'Top' if feed == 'team_home' else 'Bottom'

                    if feed in data:
                        for play in reversed(data[feed]):
                            # print(play['rowId'], play['batter'], play['pitcher'])
                            at_bat = get_ab(game, play, top_bottom_full)

                            pitch = get_pitch(at_bat, play)

                            if download_videos:
                                if not os.path.exists(pitch.video_filepath):
                                    file_url = f'{clips_base_url}away/{play["play_id"]}.mp4'

                                    myfile = requests.get(file_url, headers=headers)

                                    if not myfile.ok:
                                        print('no home')
                                        file_url = f'{clips_base_url}home/{play["play_id"]}.mp4'
                                        myfile = requests.get(file_url, headers=headers)
                                    if not myfile.ok:
                                        print('no away')
                                        file_url = f'{clips_base_url}network/{play["play_id"]}.mp4'
                                        myfile = requests.get(file_url, headers=headers)

                                    if myfile.ok:
                                        open(pitch.video_filepath, 'wb').write(myfile.content)

                                        if save_highlights and pitch.is_highlight:
                                            open(f'/Users/aadams/Downloads/2020-08-05_hou-ari/{pitch.video_filename()}',
                                                 'wb').write(myfile.content)

                                        print(f'{game_id}: Success: ({feed}): {pitch.video_filename()}')
                                    else:
                                        print(f'{game_id}: Failure ({feed}): {pitch.video_filename()}, {file_url}')

            time.sleep(interval)
            i += 1
