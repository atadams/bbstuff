from pathlib import Path

from django.core.management import BaseCommand
from django.db.models import F
from django.db.models.aggregates import Max, Min
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, clips_array
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.crop import crop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from config.settings.base import MEDIA_ROOT
from game.models import Pitch

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
        at_bat_ids = [1842]

        final_w = 500
        final_h = 400

        pitches = Pitch.objects.filter(at_bat_id__in=at_bat_ids, include_in_tipping=True).annotate(
            duration=F('pitch_release_time') - F('pitch_scene_time')).order_by('data__pitch_type',
                                                                               'data__game_total_pitches')

        pitch_aggregates = pitches.aggregate(
            Min('pitcher_height_y'),
            Max('pitcher_height_y'),
            Max('pitch_scene_time'),
            Max('pitch_release_time'),
            Min('duration'),
            Max('duration'),
        )

        final_duration = float(5.0)
        # final_duration = float(pitch_aggregates['duration__max']) + 1

        line_clip = ColorClip(size=(180, 1), color=(255, 255, 255)).set_duration(final_duration)
        line_clip_black = ColorClip(size=(180, 1), color=(0, 0, 0)).set_duration(final_duration)

        even_pitcher_height_y_max = even_number(pitch_aggregates['pitcher_height_y__max'])

        pitch_videos = []

        Path(f'{MEDIA_ROOT}/scaled_plays/{pitches[0].at_bat.game.path_name_with_id}').mkdir(parents=True, exist_ok=True)

        for pitch in pitches:
            scale = pitch_aggregates['pitcher_height_y__min'] / pitch.pitcher_height_y
            # scale = 1

            # print(pitch.video_rubber_x, pitch.video_rubber_y, pitch.pitcher_height_y, scale, )

            print(pitch.pitch_scene_time, pitch.pitch_release_time - 4)

            start_time = max(pitch.pitch_scene_time, pitch.pitch_release_time - 4)
            end_time = pitch.pitch_release_time + 1
            video_clip = VideoFileClip(pitch.video_filepath, audio=False, fps_source='fps')

            trimmed_clip = video_clip.subclip(float(start_time), float(end_time)).fx(resize, scale)

            clip_x1 = even_number((pitch.video_rubber_x * scale)) - (final_w / 2)
            clip_y1 = even_number(pitch.video_rubber_y * scale) - 220
            clip_x2 = clip_x1 + final_w
            clip_y2 = clip_y1 + even_pitcher_height_y_max + 240

            cropped_clip = crop(
                trimmed_clip,
                x1=clip_x1,
                y1=clip_y1,
                x2=clip_x2,
                y2=clip_y2,
            )

            if cropped_clip.duration != final_duration:
                freeze_duration = final_duration - cropped_clip.duration

                image_freeze = cropped_clip.to_ImageClip(duration=freeze_duration)
                bw_clip = lum_contrast(image_freeze, lum=20)
                final_clip = concatenate_videoclips([bw_clip, cropped_clip])
            else:
                final_clip = cropped_clip

            txt = TextClip(
                f'I:{pitch.at_bat.inning}  {pitch.data["pitch_type"]}',
                font='Helvetica-Narrow-Bold',
                color=PITCH_TYPE_COLORS[pitch.data["pitch_type"]], fontsize=16)

            composite_clip = CompositeVideoClip([
                final_clip,
                txt.set_position((10, 10)).set_duration(pitch_aggregates['duration__max']),
                line_clip.set_duration(final_duration).set_position((0, 30)).set_opacity(0.6),
            ])

            # print(pitch.id, 'FPS: ', composite_clip.fps, type(composite_clip.fps), type(composite_clip.duration), type(pitch.pitch_scene_time),
            #       type(pitch.pitch_release_time))

            pitch_videos.append(composite_clip)

            cropped_clip.write_videofile(
                f'/Users/aadams/Downloads/plays/{pitch.video_filename()}', fps=59.94)
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
        # final_clip = clips_array(video_array).set_duration(final_duration)
        # final_clip.write_videofile(
        #     f'/Users/aadams/Downloads/plays/final.mp4', fps=59.94)


def scale_xy(x, y, scale):
    return int(x * scale), int(y * scale)


def even_number(num):
    int_num = int(num)
    if int_num % 2 == 0:
        return int_num
    else:
        return int_num + 1
