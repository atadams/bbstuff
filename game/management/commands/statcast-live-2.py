import json
import os
import time
import urllib.request as request
from pathlib import Path

import requests
import statsapi
from dateutil.parser import parse
from django.core.management import BaseCommand

from config.settings.base import PLAY_VIDEO_ROOT
from game.utils import get_ab, get_game, get_game_statsapi, get_pitch, get_team_by_dict


def get_pbp_mlb(game_pk):
    status = {}

    with request.urlopen(f'https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live?language=en') as response:
        source = response.read()
        data = json.loads(source)

    return status


class Command(BaseCommand):
    def handle(self, *args, **options):
        interval = 2
        times = -1
        # game_id = 642090
        game_id = 641965
        download_videos = True
        save_highlights = False

        game_status = get_pbp_mlb(game_id)

        game = statsapi.get('game', {'gamePk': game_id})
        game_pbp = statsapi.get('game_playByPlay', {'gamePk': game_id})
        all_plays = game_pbp['allPlays']
        game_timestamps = statsapi.get('game_timestamps', {'gamePk': game_id})
        game_context_metrics = statsapi.get('game_contextMetrics', {'gamePk': game_id})
        game_boxscore = statsapi.get('game_boxscore', {'gamePk': game_id})
        game_content = statsapi.get('game_content', {'gamePk': game_id})
        # game_color = statsapi.get('game_color', {'gamePk': game_id})
        game_linescore = statsapi.get('game_linescore', {'gamePk': game_id})
        game_diff = statsapi.get('game_diff', {'gamePk': game_id, 'startTimecode': '20210316_172107', 'endTimecode': '20210316_172219'})

        game_scoring_play_data = statsapi.game_scoring_play_data(game_id)

        print(statsapi.notes('game_diff'))
        # print(statsapi.standings(leagueId=103, division='alw', date='09/01/2020'))

        current_play = game_pbp['currentPlay']

        current_play_data = all_plays[current_play['about']['atBatIndex']]

        for inning_number, inning in enumerate(game_pbp['playsByInning'], start=1):
            for top_bottom in ['top', 'bottom']:
                print()
                print(f'Inning {inning_number}: {top_bottom}')
                for ab_index in inning[top_bottom]:
                    atbat = all_plays[ab_index]
                    print(atbat['result']['description'])
            # print(inning)

        headers = {'referer': 'https://www.mlb.com/video/', }

        feeds = ['team_away', 'team_home']

        # home, away, network
        clips_base_url = f'https://fastball-clips.mlb.com/{game_id}/'

        i = 0

        print('game_id: ', game_id)

        while i != times:

            print('=============')
            # print(f'https://baseballsavant.mlb.com/gf?game_pk={game_id}&_=159621768973{i}')

            # with request.urlopen(f'https://baseballsavant.mlb.com/gf?game_pk={game_id}&_=15962176{i}') as response:
            with request.urlopen(f'https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live?language=en') as response:
                source = response.read()
                data = json.loads(source)
                # with open('/Users/aadams/Downloads/data3.json', 'w') as outfile:
                #     json.dump(data, outfile)

                if data['gameData']['status']['statusCode'] == 'F':
                    times = i + 1

                if 'home_team_data' in data:
                    home_team = get_team_by_dict(data['home_team_data'])
                    away_team = get_team_by_dict(data['away_team_data'])
                else:
                    home_team = get_team_by_dict(data['gameData']['teams']['home'])
                    away_team = get_team_by_dict(data['gameData']['teams']['away'])

                if 'game_date' in data:
                    game_date = parse(data['game_date'])
                elif 'originalDate' in data['gameData']['datetime']:
                    game_date = parse(data['gameData']['datetime']['originalDate'])

                game = get_game_statsapi(game_id, game_date, data['gameData']['status']['statusCode'], home_team, away_team,
                                data)

                path_name = f'{PLAY_VIDEO_ROOT}{game.path_name_with_id}'
                Path(path_name).mkdir(parents=True, exist_ok=True)

                with open(f'{path_name}/{game_id}.json', 'w') as outfile:
                    json.dump(data, outfile, indent=2)

                for play in data['liveData']['plays']['allPlays']:
                    for event in play['playEvents']:
                        if 'playId' in event:
                            filepath = f'~/Downloads/plays/{event["playId"]}.mp4'

                            if not os.path.exists(filepath):
                                file_url = f'{clips_base_url}home/{event["playId"]}.mp4'

                                myfile = requests.get(file_url, headers=headers)
                                print(myfile )

                                if myfile.ok:
                                    open(filepath, 'wb').write(myfile.content)

                            print(event)

                # for feed in feeds:
                #     top_bottom = 't' if feed == 'team_home' else 'b'
                #     top_bottom_full = 'Top' if feed == 'team_home' else 'Bottom'
                #
                #     if feed in data:
                #         for play in reversed(data[feed]):
                #             # print(play['rowId'], play['batter'], play['pitcher'])
                #             at_bat = get_ab(game, play, top_bottom_full)
                #
                #             pitch = get_pitch(at_bat, play)
                #
                #             if download_videos:
                #                 if not os.path.exists(pitch.video_filepath):
                #                     file_url = f'{clips_base_url}away/{play["play_id"]}.mp4'
                #
                #                     myfile = requests.get(file_url, headers=headers)
                #
                #                     if not myfile.ok:
                #                         print('no home')
                #                         file_url = f'{clips_base_url}home/{play["play_id"]}.mp4'
                #                         myfile = requests.get(file_url, headers=headers)
                #                     if not myfile.ok:
                #                         print('no away')
                #                         file_url = f'{clips_base_url}network/{play["play_id"]}.mp4'
                #                         myfile = requests.get(file_url, headers=headers)
                #
                #                     if myfile.ok:
                #                         open(pitch.video_filepath, 'wb').write(myfile.content)
                #
                #                         if save_highlights and pitch.is_highlight:
                #                             open(f'/Users/aadams/Downloads/2020-08-05_hou-ari/{pitch.video_filename()}',
                #                                  'wb').write(myfile.content)
                #
                #                         print(f'{game_id}: Success: ({feed}): {pitch.video_filename()}')
                #                     else:
                #                         print(f'{game_id}: Failure ({feed}): {pitch.video_filename()}, {file_url}')

            time.sleep(interval)
            i += 1
