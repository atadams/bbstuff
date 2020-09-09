from decimal import Decimal

from PIL import Image, ImageDraw
from django.core.management import BaseCommand
from django.db.models import F
from django.db.models.aggregates import Max, Min
from moviepy.video.VideoClip import ColorClip, ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from pandas import np

from game.models import Pitch
from game.utils import even_number
from game.video import max_peak_onset

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

PITCH_TYPE_COLORS_RGB = {
    'CU': (0, 209, 237, 125),
    'FF': (210, 45, 73, 125),
    'SL': (69, 170, 44, 125),
    'CH': (29, 190, 58, 125),
    'SI': (29, 190, 58, 125),
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        # at_bat_ids = [1436, 1437, 1438, 1439, 1440, 1441]
        at_bat_ids = [2438]

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
            # Min('pitcher_height_y'),
            # Max('pitcher_height_y'),
            # Max('pitch_scene_time'),
            # Max('pitch_release_time'),
            Min('duration'),
            Max('duration'),
        )

        final_duration = float(5.0)
        # final_duration = float(pitch_aggregates['duration__max']) + 1

        line_clip = ColorClip(size=(180, 1), color=(255, 255, 255)).set_duration(final_duration)
        line_clip_black = ColorClip(size=(180, 1), color=(0, 0, 0)).set_duration(final_duration)

        even_pitcher_height_y_max = even_number(pitch_aggregates['pitcher_height_y__max'])

        pitch_videos = []

        pitch_markers = []
        pitch_marker_types = []

        # Path(f'{MEDIA_ROOT}/scaled_plays/{pitches[0].at_bat.game.path_name_with_id}').mkdir(parents=True, exist_ok=True)

        pitch_count = 0

        previous_pitches = Pitch.objects.filter(at_bat__game=pitches[0].at_bat.game,
                                                data__pitcher=pitches[0].data['pitcher'],
                                                data__player_total_pitches__lt=pitches[0].data[
                                                    'player_total_pitches']).order_by('data__game_total_pitches')
        show_pitch_markers = True

        if show_pitch_markers:
            for previous_pitch in previous_pitches:
                pitch_markers.append((previous_pitch.data["px"], previous_pitch.data["pz"]))
                pitch_marker_types.append(previous_pitch.data["pitch_type"])

        for pitch in pitches:
            if Decimal(pitch.pitch_plate_time) == 0.0:
                pitch.pitch_plate_time = max_peak_onset(pitch.video_filepath)
                pitch.save()

            pitch_count += 1
            scale = pitch_aggregates['zone_w__max'] / (Decimal(pitch.crop_bottom_right_x - pitch.crop_top_left_x))
            # scale = 1

            start_time = max((pitch.pitch_release_time - Decimal(1.0)), pitch.pitch_scene_time)
            end_time = pitch.pitch_release_time + Decimal(1.2)

            if pitch_count == len(pitches):
                end_time += Decimal(2.5)

            video_clip = VideoFileClip(pitch.video_filepath, audio=False, fps_source='fps')

            trimmed_clip = video_clip.subclip(float(start_time), float(end_time)).fx(resize, float(scale))

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
            pixels_per_inch = crop_w / 17

            x1, x2 = crop_x_center - width / 2, crop_x_center + width / 2

            y1, y2 = crop_y_center - height / 2, crop_y_center + height / 2

            x1 = x1 - 140
            x2 = x2 + 110
            y1 = y1 + 70
            y2 = y2 + 90

            if show_pitch_markers:
                canvas_dots = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
                draw_dots = ImageDraw.Draw(canvas_dots)

                pitch_markers.append((pitch.data["px"], pitch.data["pz"]))
                pitch_marker_types.append(pitch.data["pitch_type"])
                color = (255, 128, 0)
                imgbase = np.zeros((trimmed_clip.h, trimmed_clip.w, 4), np.uint8)
                layer2 = np.zeros((trimmed_clip.h, trimmed_clip.w, 4))

                white_color = (255, 255, 255, 120)
                gray_color = (155, 155, 155, 120)
                light_orange = (254, 65, 55, 220)
                dark_orange = (237, 0, 0, 200)

                marker_len = 1

                for marker in pitch_markers:
                    x, y = marker
                    color = (255, 255, 255, 255) if marker_len == len(pitch_markers) else PITCH_TYPE_COLORS_RGB[
                        pitch_marker_types[marker_len - 1]]

                    dot_size = 5 if marker_len == len(pitch_markers) else 3

                    print(pitch_marker_types[marker_len - 1])

                    pitch_marker_x = int(crop_x_center - ((x * 12) * pixels_per_inch))
                    pitch_marker_y = int(Decimal(crop_scale_y2) - (
                        (Decimal(y) - Decimal(pitch.data["sz_bot"])) * Decimal(12) * Decimal(pixels_per_inch)))
                    # cv2.circle(layer2, (pitch_marker_x, pitch_marker_y), 4, color, -1, lineType=cv2.LINE_AA)

                    # if marker_len == len(pitch_markers) - 1:
                    #     res = layer2[:]  # copy the first layer into the resulting image
                    #     prev_zone_clip = ImageClip(res).set_duration(trimmed_clip.duration)
                    #     layer2 = np.zeros((trimmed_clip.h, trimmed_clip.w, 4))
                    # if marker_len == len(pitch_markers):
                    #     res = layer2[:]  # copy the first layer into the resulting image
                    #     zone_clip = ImageClip(res).set_duration(trimmed_clip.duration)
                    marker_len += 1

                    draw_dots.ellipse((pitch_marker_x - dot_size, pitch_marker_y - dot_size, pitch_marker_x + dot_size,
                                       pitch_marker_y + dot_size), color, outline=(0, 0, 0, 128))

                # canvas_dots.show()

                dots = np.array(canvas_dots)

                dots_clip = ImageClip(dots).set_duration(trimmed_clip.duration)

                # if prev_zone_clip:
                #     final_zone_clip = CompositeVideoClip([
                #         prev_zone_clip,
                #         zone_clip,
                #     ])
                # else:
                #     final_zone_clip = zone_clip

                # cv2.imwrite(f'/Users/aadams/Downloads/plays/zone_image.jpg', res)

                pitch_clip = CompositeVideoClip([
                    trimmed_clip,
                    dots_clip,
                ])
            else:
                pitch_clip = trimmed_clip

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
                txt.set_position((10, 10)).set_duration(cropped_clip.duration),
            ])

            # print(pitch.id, 'FPS: ', composite_clip.fps, type(composite_clip.fps), type(composite_clip.duration), type(pitch.pitch_scene_time),
            #       type(pitch.pitch_release_time))
            print('len: ', len(pitch_videos))
            # if len(pitch_videos) < 4 or False:
            #     pitch_videos.append(cropped_clip.set_opacity(.25))
            #     print('opacity: ', (4 - len(pitch_videos) + 1) / 5)
            # else:
            #     pitch_videos.insert(0, cropped_clip)

            pitch_videos.append(composite_clip)

            # cropped_clip.write_videofile(
            #     f'/Users/aadams/Downloads/plays/{pitch.video_filename()}', fps=59.94)

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
        # final_clip = CompositeVideoClip(pitch_videos)
        final_clip = concatenate_videoclips(pitch_videos)
        final_clip.write_videofile(
            f'/Users/aadams/Downloads/plays/ab_{pitches[0].at_bat.id}.mp4', fps=59.94)


def scale_xy(x, y, scale):
    return int(x * scale), int(y * scale)
