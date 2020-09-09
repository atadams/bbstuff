from decimal import Decimal
from pathlib import Path
from random import randrange

from django.core.management import BaseCommand
from moviepy.video.io.VideoFileClip import VideoFileClip

from config.settings.base import MEDIA_ROOT
from game.models import Pitch


class Command(BaseCommand):
    def handle(self, *args, **options):
        Path(f'{MEDIA_ROOT}/training-images/').mkdir(parents=True, exist_ok=True)
        pitches = Pitch.objects.filter(pitch_release_time__gt=0)

        print(len(pitches))

        for pitch in pitches:
            frame_time = pitch.pitch_release_time + Decimal(randrange(1, 12) / 100)
            print(pitch.id, pitch.pitch_release_time, frame_time)
            video_clip = VideoFileClip(pitch.video_filepath, audio=False, fps_source='fps')
            video_clip.save_frame(f'{MEDIA_ROOT}/training-images/{pitch.id}.png', t=float(frame_time))
