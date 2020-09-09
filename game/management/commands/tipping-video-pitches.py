from decimal import Decimal

import numpy as np
import cv2
from django.core.management import BaseCommand
from django.db.models import F
from django.db.models.aggregates import Max, Min
from moviepy.video.VideoClip import ColorClip, ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.drawing import circle, color_gradient

from game.models import Pitch
from game.utils import even_number

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
        # at_bat_ids = [1436, 1437, 1438, 1439, 1440, 1441]
        at_bat_ids = [2379]

        final_w = 500
        final_h = 400

        pitches = Pitch.objects.filter(at_bat_id__in=at_bat_ids, include_in_tipping=True).annotate(
            duration=F('pitch_release_time') - F('pitch_scene_time')).order_by('data__game_total_pitches')

        pitches_agg = Pitch.objects.filter(at_bat_id__in=at_bat_ids, include_in_tipping=True).annotate(
            duration=F('pitch_release_time') - F('pitch_scene_time'),
            zone_w=F('crop_bottom_right_x') - F('crop_top_left_x'),
            zone_h=F('crop_bottom_right_y') - F('crop_top_left_y')).order_by('data__game_total_pitches')

        pitch_aggregates = pitches_agg.aggregate(
            Min('zone_w'),
            Max('zone_w'),
            Min('zone_h'),
            Max('zone_h'),
            Min('pitcher_height_y'),
            Max('pitcher_height_y'),
            Max('pitch_scene_time'),
            Max('pitch_release_time'),
            Min('duration'),
            Max('duration'),
        )

        img = np.zeros((512, 512, 3), np.uint8)

        # print(pitches[0].crop_top_left_x, pitches[0].crop_top_left_y)
        # print(pitches[0].crop_bottom_right_x, pitches[0].crop_bottom_right_y)
        print(pitch_aggregates['zone_w__max'])

        final_duration = float(4.0)
        # final_duration = float(pitch_aggregates['duration__max']) + 1

        line_clip = ColorClip(size=(180, 1), color=(255, 255, 255)).set_duration(final_duration)
        line_clip_black = ColorClip(size=(180, 1), color=(0, 0, 0)).set_duration(final_duration)

        even_pitcher_height_y_max = even_number(pitch_aggregates['pitcher_height_y__max'])

        pitch_videos = []
        pitch_markers = []

        # Path(f'{MEDIA_ROOT}/scaled_plays/{pitches[0].at_bat.game.path_name_with_id}').mkdir(parents=True, exist_ok=True)

        for pitch in pitches:
            temp = pitch.zone_coordinates
            temp_tl, temp_br = pitch.zone_coordinates
            (tl_x, tl_y), (br_x, bl_x) = pitch.zone_coordinates
            scale = pitch_aggregates['zone_w__max'] / (Decimal(pitch.crop_bottom_right_x - pitch.crop_top_left_x))
            print(pitch_aggregates['zone_w__max'], Decimal(pitch.crop_bottom_right_x - pitch.crop_top_left_x), scale)
            # scale = 1
            print(scale)

            start_time = pitch.pitch_release_time - Decimal(0.425)
            end_time = pitch.pitch_release_time + Decimal(1.0)
            video_clip = VideoFileClip(pitch.video_filepath, audio=False, fps_source='fps')

            trimmed_clip = video_clip.subclip(float(start_time), float(end_time)).fx(resize, float(scale))

            zone_x1 = even_number((pitch.zone_top_left_x * scale))
            zone_y1 = even_number(pitch.zone_top_left_y * scale)
            zone_x2 = even_number((pitch.zone_bottom_right_x * scale))
            zone_y2 = even_number(pitch.zone_bottom_right_y * scale)

            zone_width = zone_x2 - zone_x1
            pixels_per_inch = zone_width / 17

            zone_center_x = zone_x1 + (zone_width / 2)

            pitch_markers.append((pitch.data["px"], pitch.data["pz"]))
            color = (255, 128, 0)
            imgbase = np.zeros((trimmed_clip.h, trimmed_clip.w, 4), np.uint8)
            img = cv2.rectangle(imgbase, (zone_x1, zone_y1), (zone_x2, zone_y2), color, 3)

            # create 3 separate BGRA images as our "layers"
            layer1 = np.zeros((trimmed_clip.h, trimmed_clip.w, 4))
            layer2 = np.zeros((trimmed_clip.h, trimmed_clip.w, 4))
            # layer3 = np.zeros((trimmed_clip.h, trimmed_clip.w, 4))

            # draw a red circle on the first "layer",
            # a green rectangle on the second "layer",
            # a blue line on the third "layer"
            red_color = (0, 0, 255, 255)
            green_color = (255, 255, 255, 255)
            blue_color = (255, 0, 0, 255)
            white_color = (255, 255, 255, 255)
            gray_color = (155, 155, 155, 220)
            marker_len = 1

            font = cv2.FONT_HERSHEY_SIMPLEX
            for marker in pitch_markers:
                x, y = marker
                color = white_color if marker_len == len(pitch_markers) else gray_color

                pitch_marker_x = int(zone_center_x - ((x * 12) * pixels_per_inch))
                pitch_marker_y = int(zone_y2 - ((y - pitch.data["sz_bot"]) * 12 * pixels_per_inch))
                cv2.circle(layer2, (pitch_marker_x, pitch_marker_y), 5, color, 1, cv2.FILLED)
                # cv2.putText(layer2, pitch.data['start_speed'], (pitch_marker_x + 10, pitch_marker_y), font, 4, color, 2,
                #             cv2.LINE_AA)
                # cv2.putText(layer2, f'{pitch.data["start_speed"]}', (pitch_marker_x + 8, pitch_marker_y + 3), font, 0.4, color, 1, cv2.LINE_AA, False)
                marker_len += 1
            # cv2.circle(layer2, (int(pitch_marker_x), int(pitch_marker_y)), 5, white_color, 1, cv2.FILLED)
            # cv2.rectangle(layer1, (zone_x1, zone_y1), (zone_x2, zone_y2), blue_color, 1)
            # cv2.line(layer3, (170, 170), (340, 340), blue_color, 5)

            res = layer2[:]  # copy the first layer into the resulting image

            # copy only the pixels we were drawing on from the 2nd and 3rd layers
            # (if you don't do this, the black background will also be copied)
            # cnd = layer2[:, :, 3] > 0
            # res[cnd] = layer2[cnd]
            # cnd = layer3[:, :, 3] > 0
            # res[cnd] = layer3[cnd]

            # res = img[:]
            # cnd = img[:, :, 3] > 0
            # res[cnd] = img[cnd]
            zone_clip = ImageClip(res).set_duration(trimmed_clip.duration)

            cv2.imwrite(f'/Users/aadams/Downloads/plays/zone_image.jpg', res)

            w, h = trimmed_clip.size
            clip = trimmed_clip
            location_center = (zone_x1, zone_y1)
            print(trimmed_clip.h, trimmed_clip.w, zone_x1, zone_y1)

            offset = 0

            # grad = color_gradient(clip.size, p1=(0, 2 * h / 3),
            #                       p2=(0, h / 4), col1=0.0, col2=1.0)
            #
            # test2 = color_gradient((clip.w, clip.h), p1=(clip.w / 2, clip.h / 4), r=3, col1=1.0,
            #               col2=0.0, shape='radial', offset=offset)
            #
            # test = circle(screensize=(clip.w, clip.h), center=(clip.w / 2, clip.h / 4),
            #        radius=4.0,  col1=1, col2=0, blur=4)
            #
            # location_clip = circle(screensize=(720, 1280), center=(620, 252), radius=4, blur=0)

            # pitch_markers.append(zone_clip)
            #
            # pitch_markers_composite = CompositeVideoClip(pitch_markers)
            pitch_clip = CompositeVideoClip([
                trimmed_clip,
                # zone_clip,
            ])

            # pitch_clip.write_videofile(
            #     f'/Users/aadams/Downloads/plays/clip_{pitch.video_filename()}', fps=59.94)

            clip_x1 = even_number((pitch.crop_top_left_x * scale))
            clip_y1 = even_number(pitch.crop_top_left_y * scale)
            clip_x2 = clip_x1 + pitch_aggregates['zone_w__max']
            clip_y2 = clip_y1 + pitch_aggregates['zone_h__max']

            # clip_x1 = even_number(pitches[0].crop_top_left_x * scale)
            # clip_y1 = even_number(pitches[0].crop_top_left_y * scale) - 30
            # clip_x2 = even_number(pitches[0].crop_bottom_right_x * scale)
            # clip_y2 = even_number(pitches[0].crop_bottom_right_y * scale) + 30

            # cropped_clip = crop(
            #     trimmed_clip,
            #     x1=clip_x1,
            #     y1=clip_y1,
            #     x2=clip_x2,
            #     y2=clip_y2,
            # )

            crop_scale_x1 = pitch.zone_top_left_x * scale
            crop_scale_y1 = pitch.zone_top_left_y * scale
            crop_scale_x2 = pitch.zone_bottom_right_x * scale
            crop_scale_y2 = pitch.zone_bottom_right_y * scale
            crop_w = even_number(crop_scale_x2 - crop_scale_x1)
            crop_h = even_number(crop_scale_y2 - crop_scale_y1)
            crop_x_center = even_number(float(crop_scale_x1) + (crop_w / 2))
            crop_y_center = even_number(float(crop_scale_y1) + (crop_h / 2))

            width = even_number(pitch_aggregates['zone_w__max'])
            height = even_number(pitch_aggregates['zone_h__max'])

            x1, x2 = crop_x_center - width / 2, crop_x_center + width / 2

            y1, y2 = crop_y_center - height / 2, crop_y_center + height / 2

            x1 = x1 - 140
            x2 = x2 + 110
            y1 = y1 + 70
            y2 = y2 + 70

            cropped_clip = crop(
                pitch_clip,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )

            # cropped_clip = crop(trimmed_clip, x_center=crop_x_center, y_center=crop_y_center,
            #                     width=even_number(pitch_aggregates['zone_w__max']),
            #                     height=even_number(pitch_aggregates['zone_h__max']))

            # if cropped_clip.duration != final_duration:
            #     freeze_duration = final_duration - cropped_clip.duration
            #
            #     image_freeze = cropped_clip.to_ImageClip(duration=freeze_duration)
            #     bw_clip = lum_contrast(image_freeze, lum=20)
            #     final_clip = concatenate_videoclips([bw_clip, cropped_clip])
            # else:
            #     final_clip = cropped_clip

            txt = TextClip(
                f'{pitch.data["pre_balls"]}-{pitch.data["pre_strikes"]}  {pitch.data["start_speed"]} MPH  {pitch.data["pitch_name"]}',
                font='Helvetica-Bold',
                color='White', fontsize=22)

            composite_clip = CompositeVideoClip([
                cropped_clip,
                # txt.set_position((10, 10)).set_duration(cropped_clip.duration),
            ])

            # print(pitch.id, 'FPS: ', composite_clip.fps, type(composite_clip.fps), type(composite_clip.duration), type(pitch.pitch_scene_time),
            #       type(pitch.pitch_release_time))
            if len(pitch_videos) < 3:
                pitch_videos.append(cropped_clip.set_opacity(.33))
                print('opacity: ', (3 - len(pitch_videos) + 1) / 4)
            else:
                pitch_videos.insert(0, cropped_clip)

            # pitch_videos.append(composite_clip)

            # composite_clip.write_videofile(
            #     f'/Users/aadams/Downloads/plays/{pitch.video_filename()}', fps=59.94)
        #
        # print(len(pitch_videos))
        #
        # video_array = [
        #     [
        #         pitch_videos[0],
        #         pitch_videos[1],
        #         pitch_videos[2],
        #         pitch_videos[3],
        #         pitch_videos[4],
        #         pitch_videos[5],
        #         pitch_videos[6],
        #         pitch_videos[7],
        #         pitch_videos[8],
        #     ],
        #     [
        #         pitch_videos[9],
        #         pitch_videos[10],
        #         pitch_videos[11],
        #         pitch_videos[12],
        #         pitch_videos[13],
        #         pitch_videos[14],
        #         pitch_videos[15],
        #         pitch_videos[16],
        #         pitch_videos[17],
        #     ], [
        #         pitch_videos[18],
        #         pitch_videos[19],
        #         pitch_videos[20],
        #         pitch_videos[21],
        #         pitch_videos[22],
        #         pitch_videos[23],
        #         pitch_videos[24],
        #         line_clip_black,
        #         line_clip_black,
        #     ],
        # ]
        #
        final_clip = CompositeVideoClip(pitch_videos)
        #
        # final_clip = concatenate_videoclips(pitch_videos)
        final_clip.write_videofile(
            f'/Users/aadams/Downloads/plays/ab_{pitches[0].at_bat.id}.mp4', fps=59.94)


