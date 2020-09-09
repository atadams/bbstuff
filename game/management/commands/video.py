from django.core.management import BaseCommand
from django.db.models import F
from django.db.models.aggregates import Max, Min
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

from game.models import Pitch


class Command(BaseCommand):
    def handle(self, *args, **options):
        pitches = Pitch.objects.filter(at_bat_id=1842).annotate(duration=F('pitch_release_time') - F('pitch_scene_time'))

        pitch_aggregates = pitches.aggregate(
            Min('pitcher_height_y'),
            Max('pitch_scene_time'),
            Max('pitch_release_time'),
            Min('duration'),
            Max('duration'),
        )

        for pitch in pitches:
            scale = pitch_aggregates['pitcher_height_y__min'] / pitch.pitcher_height_y
            print(pitch.video_rubber_x, pitch.video_rubber_y, pitch.pitcher_height_y, scale, )
            scale_x, scale_y = scale_xy(pitch.video_rubber_x, pitch.video_rubber_y, scale)
            print(scale_x, scale_y)
            start_time = pitch.pitch_release_time - 2
            end_time = pitch.pitch_release_time + 1
            video_clip = VideoFileClip(pitch.video_filepath, audio=False).fx(resize, scale)
            # video_clip = VideoFileClip(pitch.video_filepath)
            scaled_clip = video_clip.subclip(float(start_time), float(end_time))
            # scaled_clip = video_clip

            clip_x1 = (pitch.video_rubber_x * scale) - 280
            clip_y1 = (pitch.video_rubber_y - pitch.pitcher_height_y) * scale - 300
            clip_x2 = clip_x1 + 650
            clip_y2 = (pitch.video_rubber_y * scale) + 100

            cropped_clip = crop(
                scaled_clip,
                x1=clip_x1,
                y1=clip_y1,
                x2=clip_x2,
                y2=clip_y2,
            )

            temp = even_size(cropped_clip)

            temp.write_videofile(pitch.scaled_video_filepath, fps=59.94)

            # if scale != 1:
            #     video_clip.resize(scale)
            # else:
            #     resized_clip = video_clip
            # print(video_clip.h, scaled_clip.h)
            # video_clip.close()
        print(len(pitches))


def scale_xy(x, y, scale):
    return int(x * scale), int(y * scale)
