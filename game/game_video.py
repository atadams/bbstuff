from decimal import Decimal

import librosa
from moviepy.video.fx.crop import crop
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from pandas import np


def get_pitch_video(pitch_obj, prerelease_seconds=0, duration=None, video_scale=1.0, crop_w=560, crop_h=560,
                    crop_center_x=None, crop_center_y=None, adjust_x=0, adjust_y=0):
    start_time = max(float(pitch_obj.pitch_release_time) - prerelease_seconds, float(pitch_obj.pitch_scene_time))
    end_time = float(start_time + duration) if duration else None

    pitch_video = VideoFileClip(pitch_obj.video_filepath, audio=False, fps_source='fps').subclip(start_time, end_time)

    center_x = pitch_video.w / 2 if not crop_center_x else crop_center_x
    center_y = pitch_video.h / 2 if not crop_center_y else crop_center_y

    center_x = even_number(center_x * float(video_scale) - adjust_x)
    center_y = even_number(center_y * float(video_scale) - adjust_y)

    if video_scale != 1.0:
        pitch_video = pitch_video.fx(resize, float(video_scale))
    else:
        pitch_video = pitch_video

    pitch_video = crop(pitch_video, x_center=center_x, y_center=center_y, width=crop_w, height=crop_h)

    return pitch_video


def scale_xy(x, y, scale_amt):
    return int(x * scale_amt), int(y * scale_amt)


def max_peak_onset(filepath, offset=0, hop_length=512, sr=22050):
    y, sr = librosa.load(
        filepath,
        offset=offset,
        sr=sr,
    )

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)

    return times[np.argmax(onset_env)] + offset


def even_number(num):
    int_num = int(num)
    if int_num % 2 == 0:
        return int_num
    else:
        return int_num + 1

#
# def scale():
#     pass
#
#
# def crop():
#     pass
#
#
# def pan():
#     pass
