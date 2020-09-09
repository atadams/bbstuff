from decimal import Decimal
from pathlib import Path

import requests
from django.core.management import BaseCommand
from django.db.models import F
from django.db.models.aggregates import Max, Min
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from config.settings.base import PLAY_VIDEO_ROOT
from game.models import AtBat, Pitch, Player

PITCH_TYPE_COLORS = {
    'CU': 'LightGreen',
    'KC': 'LightGoldenrod',
    'SC': 'gray',
    'SL': 'LightSeaGreen',
    'CH': 'Pink',
    'KN': 'LightGreen',
    'EP': 'LightGreen',
    'FC': 'LightCoral',
    'FF': 'LightBlue',
    'FS': 'LightSalmon',
    'FT': 'LightSkyBlue',
    'SI': 'LightSteelBlue',
    'FO': 'gray',
    'PO': 'gray',
    'IN': 'gray',
    'UN': 'gray',
    'AB': 'gray',
    'FA': 'gray',
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        download_videos = True
        headers = {'referer': 'https://www.mlb.com/video/', }
        player = Player.objects.get(name_first_last='Kyle Tucker')
        at_bats = player.batter.filter(game__date__gt='2020-07-27', game__date__lt='2020-08-14',
                                       game__home_team__abbreviation='HOU').order_by('game__date', 'ab_number')

        print(f'At-bats: {len(at_bats)}')

        video_array = []

        if download_videos:
            for at_bat in at_bats:
                path_name = f'{PLAY_VIDEO_ROOT}{at_bat.game.path_name_with_id}'
                Path(path_name).mkdir(parents=True, exist_ok=True)
                for pitch in at_bat.pitches.all().order_by('row_id'):
                    if not pitch.video_exists:
                        myfile = requests.get(pitch.mlb_video_url_astros, headers=headers)

                        if not myfile.ok:
                            myfile = requests.get(pitch.mlb_video_url_home, headers=headers)
                        if not myfile.ok:
                            myfile = requests.get(pitch.mlb_video_url_away, headers=headers)
                        if not myfile.ok:
                            myfile = requests.get(pitch.mlb_video_url_network, headers=headers)

                        if myfile.ok:
                            open(pitch.video_filepath, 'wb').write(myfile.content)

                            print(
                                f'Success: {pitch.at_bat.game.game_description_full_date} {pitch.at_bat.inning_string} {pitch.row_id}')
                        else:
                            print(
                                f'FAILED: {pitch.at_bat.game.game_description_full_date} {pitch.at_bat.inning_string} {pitch.row_id}')

            print('Downloads Complete!')

        for at_bat in at_bats:
            for pitch in at_bat.pitches.all().order_by('row_id'):

                if pitch.video_exists:
                    print(f'{pitch.at_bat.game.game_description_full_date} {pitch.at_bat.inning_string} {pitch.row_id}')
                    video_clip = VideoFileClip(pitch.video_filepath, audio=False, fps_source='fps')

                    txt = TextClip(
                        f'{pitch.at_bat.game.game_description_full_date}',
                        font='Helvetica-Bold', color='white', fontsize=32)

                    composite_clip = CompositeVideoClip([
                        video_clip,
                        txt.set_position((10, 10)).set_duration(video_clip.duration),
                    ])

                    video_array.append(composite_clip)

        final_clip = concatenate_videoclips(video_array)
        final_clip.write_videofile(
            f'/Users/aadams/Downloads/plays/{player.clean_name}.mp4', fps=59.94)


def scale_xy(x, y, scale):
    return int(x * scale), int(y * scale)


def even_number(num):
    int_num = int(num)
    if int_num % 2 == 0:
        return int_num
    else:
        return int_num + 1
