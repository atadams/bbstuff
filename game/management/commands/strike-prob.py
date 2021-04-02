import csv
from decimal import Decimal

import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.core.management import BaseCommand
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize
from moviepy.video.fx.freeze import freeze
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from game import game_video
from game.game_video import max_peak_onset
from game.graphics import strike_zone_block
from game.models import Pitch
# zone size 17 x 24 inches. 18.5 inches above ground
# sz_top = 3.5, sz_bot = 1.5
from game.utils import progress

game_ids = [630220, 630438, 630860, 630867, 630904, 630983, 630984, 631007, 631071, 631096, 631149, 631152,
            631160, 631211, 631429, 631460, 631559, 631615]


class Command(BaseCommand):
    def handle(self, *args, **options):

        # export_csv, import_csv, write_video
        action = 'write_pitch'

        if action == 'export_csv':
            pitches = Pitch.objects.filter(at_bat__game_id__in=game_ids).order_by('at_bat__game_id',
                                                                                  'data__game_total_pitches')

            all_rows = []

            for i, pitch in enumerate(pitches):
                # print(f'{i} of {len(pitches)}')
                all_rows.append([pitch.id, pitch.data['px'], pitch.data['pz']])

            df = pd.DataFrame(all_rows, columns=['pitch_id', 'px', 'py'])
            df.to_csv('/Users/aadams/Downloads/called_strike/pitch_cs.csv')

        if action == 'import_csv':
            with open('/Users/aadams/Downloads/called_strike/pitch_cs_w_probs.csv') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0

                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    else:
                        print(row[2])
                        pitch = Pitch.objects.get(id=row[2])
                        pitch.strike_probability = row[5]
                        pitch.save()
                print(f'Processed {line_count} lines.')

        if action == 'write_video':
            zone_images = []
            pitches = Pitch.objects.filter(at_bat__game_id__in=game_ids,
                                           data__description__in=['Ball', 'Called Strike'],
                                           strike_probability__isnull=False).order_by('-strike_probability',
                                                                                      'data__game_total_pitches')

            print(len(pitches))

            prev_probabilities = []

            print()

            all_clips = False

            pitch_cnt = 0

            for i, pitch in enumerate(pitches):
                # print(abs(pitch.data['px']), pitch.in_zone)
                # if not (pitch.strike_probability == 0.0 and pitch.data['description'] == 'Ball'):
                if (pitch.in_zone and pitch.data['description'] == 'Ball') or (
                    not pitch.in_zone and pitch.data['description'] == 'Called Strike'):
                    progress(i, len(pitches), f'Generating probability video')
                    dot_hue = 220 - int(220 * pitch.strike_probability)
                    dot_color = f'hsl({dot_hue}, 100%, 50%)'
                    prev_probabilities.append([pitch.data['px'], pitch.data['pz'], pitch.data['call'], dot_color])

                    zone_image = strike_zone_block(pitch_array=prev_probabilities, final_width=600)
                    zone_images.append(pd.np.array(zone_image))
                    pitch_cnt += 1

            print()

            print(pitch_cnt)
            clip = ImageSequenceClip(zone_images, fps=119.88)

            clip.write_videofile(
                f'/Users/aadams/Downloads/plays/strike_prob_4.mp4', fps=59.94)

        if action == 'write_pitch':
            # game_ids = [631615]
            # pitch = Pitch.objects.filter(at_bat__game_id__in=game_ids,
            #                                data__description__in=['Called Strike'],
            #                                strike_probability__isnull=False).order_by('strike_probability',
            #                                                                           'data__game_total_pitches').first()

            pitch = Pitch.objects.get(id=16963)

            if Decimal(pitch.pitch_plate_time) == 0.0:
                pitch.pitch_plate_time = max_peak_onset(pitch.video_filepath)
                if pitch.pitch_release_time == 0.0:
                    pitch.pitch_release_time = max(pitch.pitch_plate_time - 0.5, 1.5)
                pitch.save()

            pitch_duration = 5.0
            scale = 1.0

            print(pitch.at_bat.game_id, pitch.id, pitch.strike_probability, pitch.pitch_plate_time, pitch.video_filepath)

            pitch_video = game_video.get_pitch_video(
                pitch,
                crop_w=720,
                prerelease_seconds=1.5,
                duration=pitch_duration,
                video_scale=scale,
                crop_center_x=pitch.zone_center_x,
                crop_center_y=pitch.zone_center_y,
                adjust_x=50,
                adjust_y=-80,
            )

            prob_image = Image.open('/Volumes/LaCie/Sites/statcast/statcast/media/cs/called-strike_zone_clean.png')
            prob_image = prob_image.resize((279, 201))

            # zone_image = strike_zone_block(
            #     pitch.data['sz_top'],
            #     pitch.data['sz_bot'],
            #     attack_zone_image=prob_image,
            #     # break_x=float(pitch.data["calc_break_x"]),
            #     # break_z=float(pitch.data["calc_break_z_induced"]),
            # )

            zone_clip = ImageClip(pd.np.array(prob_image)).set_duration(7.0).set_opacity(0.5)
            # zone_clip = zone_clip.fx(resize, (279, 201))

            start_time = max(float(pitch.pitch_release_time) - 1.5, float(pitch.pitch_scene_time))
            freeze_time = float(pitch.pitch_plate_time) - start_time

            frozen_video = freeze(pitch_video, t=freeze_time, freeze_duration=3)

            pitch_video = CompositeVideoClip([
                frozen_video,
                zone_clip,
            ])

            pitch_video.write_videofile(
                f'/Users/aadams/Downloads/plays/strike_prob_2_5.mp4', fps=59.94)
