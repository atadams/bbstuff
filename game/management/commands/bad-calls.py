from decimal import Decimal

from django.core.management import BaseCommand
from moviepy.video.compositing.concatenate import concatenate_videoclips

from game import game_video
from game.game_video import max_peak_onset
from game.models import AtBat, Pitch


class Command(BaseCommand):
    def handle(self, *args, **options):
        game_id = 631550

        pitches = Pitch.objects.filter(at_bat__game_id=game_id)

        # for pitch in pitches:
        #     if Decimal(pitch.pitch_plate_time) == 0.0:
        #         pitch.pitch_plate_time = max_peak_onset(pitch.video_filepath)
        #         pitch.pitch_release_time = max(pitch.pitch_plate_time - 0.5, 1.5)
        #         pitch.save()

        video_array = []

        print('platex_w: 0.79167')

        plate_w_from_center = 0.708333333
        ball_in_feet = 0.05

        print('ball_in_feet:', ball_in_feet)
        i = 0
        abn = 0
        for pitch in pitches:
            if pitch.data['ab_number'] != abn:
                abn = pitch.data['ab_number']
                # print('------------------')

            high = True if pitch.data['pz'] > pitch.data['sz_top'] + ball_in_feet else False
            low = True if pitch.data['pz'] < pitch.data['sz_bot'] - ball_in_feet else False
            wide = True if abs(pitch.data['px']) > plate_w_from_center + ball_in_feet else False

            is_ball = True if high or low or wide else False
            is_strike = False if is_ball else True
            called_strike = True if pitch.data['description'] == 'Called Strike' else False
            called_ball = True if pitch.data['description'] == 'Ball' else False

            bad_call = True if (is_ball and called_strike) or (is_strike and called_ball) else False

            if bad_call:
                i += 1
                # print(
                #     i,
                #     pitch.id,
                #     pitch.data['description'],
                #     '  b:', is_ball,
                #     '  s:', is_strike,
                #     '  w:', wide,
                #     '  h:', high,
                #     '  l:', low,
                #     '  px:', abs(pitch.data['px']),
                #     '  plt:', plate_w_from_center,
                #     '  plt+b:', plate_w_from_center - ball_in_feet,
                #     '  pz:', pitch.data['pz'],
                #     '  zt:', pitch.data['sz_top'],
                #     '  zt+b:', pitch.data['sz_top'] - ball_in_feet,
                #     '  zb:', pitch.data['sz_bot'],
                #     '  zb+b:', pitch.data['sz_bot'] + ball_in_feet,
                # )

                print(pitch.data['px'], pitch.data['pz'], pitch.data['description'], sep=',')
                print(pitch.id, pitch.pitch_release_time)
                if pitch.pitch_release_time > 1.5:
                    pitch_video = game_video.get_pitch_video(
                        pitch,
                        crop_w=720,
                        prerelease_seconds=0.5,
                        duration=3.0,
                        video_scale=1.0,
                        crop_center_x=pitch.zone_center_x,
                        crop_center_y=pitch.zone_center_y,
                        adjust_x=70,
                        adjust_y=-80,
                    )
                    video_array.append(pitch_video)

        if len(video_array):
            final_clip = concatenate_videoclips(video_array)
            final_clip.write_videofile(
                f'/Users/aadams/Downloads/plays/bad-calls_{game_id}.mp4', fps=59.94)
