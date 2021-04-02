from decimal import Decimal

import matplotlib.pyplot as plt
import statsapi
from django.core.management import BaseCommand
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from pandas import np, qcut

from game import game_video
from game.graphics import attack_zones, inning_count_block, matchup_block, pitch_display_lg, player_name_block, \
    strike_zone_block, \
    text_image
from game.models import Pitch, get_pitch_aggregates, get_pitches_by_at_bat_ids, get_pitches_by_ids


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            nargs='?',
            default='seq'
        )

        parser.add_argument(
            '--atbat_ids',
            nargs='+',
            type=int,
            help='At_Bat IDs',
        )

        parser.add_argument(
            '--pitch_ids',
            nargs='+',
            type=int,
            help='Pitch IDs',
        )

        parser.add_argument(
            '--show-pitch-data',
        )

    def handle(self, *args, **options):

        colors_array = [
            'hsl(240, 100%, 50%)',
            'hsl(240, 100%, 55%)',
            'hsl(240, 100%, 60%)',
            'hsl(240, 100%, 65%)',
            'hsl(240, 100%, 70%)',
            'hsl(240, 100%, 75%)',
            'hsl(240, 100%, 80%)',
            'hsl(240, 100%, 85%)',
            'hsl(240, 100%, 90%)',
            'hsl(240, 100%, 95%)',
            'hsl(0, 0%, 100%)',
            'hsl(0, 100%, 95%)',
            'hsl(0, 100%, 90%)',
            'hsl(0, 100%, 85%)',
            'hsl(0, 100%, 80%)',
            'hsl(0, 100%, 75%)',
            'hsl(0, 100%, 70%)',
            'hsl(0, 100%, 65%)',
            'hsl(0, 100%, 60%)',
            'hsl(0, 100%, 55%)'
        ]
        # zonedata = vStrikeZoneData(hotColdZones(514888))
        #
        # player_stat_data = get_player_stats(425844)
        # meta = statsapi.get('game_playByPlay', {'gamePk': 631164})
        # meta2 = statsapi.meta('statGroups')
        # meta3 = statsapi.meta('statTypes')
        # arsenal = get_pitch_arsenal(425844)
        # print(meta)

        options['atbat_ids'] = [7575, ]
        options['show-pitch-data'] = True
        options['show-zone-data'] = True
        options['show-attack-zones'] = False
        options['sidebar_width'] = 120
        options['sidebar_element_spacing'] = 10
        display_inning_count_block = False
        display_previous_velo = False
        display_matchup_block = True
        display_attack_zones = False
        only_final_pitch_of_ab = False
        prev_final_pitch = None

        pitches = None
        if options['atbat_ids']:
            pitches = get_pitches_by_at_bat_ids(options['atbat_ids'])
        elif options['pitch_ids']:
            pitches = get_pitches_by_ids(options['pitch_ids'])

        if pitches:
            pitch_agg = get_pitch_aggregates(pitches.values_list('id', flat=True))

            if options['type'] == 'seq':
                last_pitches_array = []
                video_array = []
                pitches_zone = []

                at_bat_id = None
                matchup_clip = None
                count_clip = None
                zone_clip = None
                attack_clip = None

                print(pitch_agg['zone_w__max'])

                for i, pitch in enumerate(pitches):
                    next_y = 0
                    pitch_data_clip = None
                    video_elements = []

                    # scale = Decimal(pitch.zone_w) / pitch_agg['zone_w__max']
                    scale = 0.8
                    if only_final_pitch_of_ab:
                        pitch_duration = 2.0
                    else:
                        pitch_duration = 6 if i == len(pitches) - 1 else 2.5

                    pitch_video = game_video.get_pitch_video(
                        pitch,
                        crop_w=840,
                        prerelease_seconds=0.5,
                        duration=pitch_duration,
                        video_scale=scale,
                        crop_center_x=pitch.zone_center_x,
                        crop_center_y=pitch.zone_center_y,
                        adjust_x=50,
                        adjust_y=-40,
                    )

                    video_elements.append(pitch_video)

                    # If new at-bat. Only create batter graphics once per AB.
                    if at_bat_id != pitch.at_bat.id:
                        batter_zone_top, batter_zone_bottom = pitch.at_bat.batter.zone_top_bottom
                        at_bat_id = pitch.at_bat_id
                        pitches_zone = []

                    # MATCHUP CLIP
                    if display_matchup_block:
                        matchup_block_image = matchup_block(
                            pitch.at_bat.pitcher,
                            pitch.at_bat.team_pitching,
                            pitch.at_bat.batter,
                            pitch.at_bat.team_batting,
                        )

                        matchup_clip = ImageClip(np.array(matchup_block_image)).set_duration(pitch_video.duration)

                    # INNING/COUNT CLIP
                    if display_inning_count_block:
                        print(pitch.play_id, pitch.runners_str)
                        count_image = inning_count_block(
                            inning=pitch.at_bat.inning,
                            top_bottom=pitch.at_bat.top_bottom,
                            balls=pitch.balls,
                            strikes=pitch.strikes,
                            outs=min(0, pitch.outs - 1),
                            runners_str=pitch.runners_str,
                        )

                        count_clip = ImageClip(np.array(count_image)).set_duration(pitch_video.duration)

                    # PITCH DATA CLIP
                    if options['show-pitch-data']:
                        pitch_data_image = pitch_display_lg(
                            pitch.data['pitch_name'],
                            pitch.data['start_speed'],
                            # outcome=pitch.pitch_result,
                            width=options['sidebar_width'],
                        )
                        pitch_data_clip = ImageClip(np.array(pitch_data_image)).set_duration(pitch_video.duration)

                    # ATTACK ZONES
                    data_colors = []
                    if options['show-attack-zones']:
                        batter_ba_zone_data = pitch.at_bat.batter.ba_dataframe(year='2019', p_throws=pitch.data['p_throws'], pitch_type=pitch.data['pitch_type'])
                        batter_ba_zone_data = batter_ba_zone_data.fillna(0)
                        data_bins = qcut(batter_ba_zone_data.ba, 20, labels=False, duplicates='drop')

                        for cnt, idx in enumerate(data_bins, start=1):
                            data_colors.append(colors_array[idx])

                        # attack_zones_image = attack_zones(w=pitch.zone_w * 4, h=pitch.zone_h * 4, zones=data_colors)
                        #
                        # attack_clip = ImageClip(np.array(attack_zones_image)).set_duration(pitch_video.duration)

                    # STRIKE ZONE CLIP
                    if options['show-zone-data']:
                        pitches_zone.append([pitch.data['px'], pitch.data['pz'], pitch.data['call']])
                        zone_image = strike_zone_block(
                            batter_zone_top,
                            batter_zone_bottom,
                            pitch_array=pitches_zone,
                            call=pitch.pitch_result,
                            attack_zones_data=data_colors,
                        )
                        zone_clip = ImageClip(np.array(zone_image)).set_duration(pitch_video.duration)

                    if matchup_clip:
                        next_y += options['sidebar_element_spacing']
                        video_elements.append(matchup_clip.set_position((5, next_y)))
                        next_y += matchup_clip.h

                    if count_clip:
                        next_y += options['sidebar_element_spacing']
                        video_elements.append(count_clip.set_position((5, next_y)))
                        next_y += count_clip.h

                    if pitch_data_clip:
                        next_y += options['sidebar_element_spacing']
                        video_elements.append(pitch_data_clip.set_position((5, next_y)))
                        next_y += pitch_data_clip.h

                    if zone_clip:
                        next_y += options['sidebar_element_spacing']
                        video_elements.append(zone_clip.set_position((5, next_y)))

                    pitch_video = CompositeVideoClip(video_elements)

                    video_array.append(pitch_video)

                if only_final_pitch_of_ab:
                    current_ab = pitches[0].at_bat.id
                    for i, pitch in enumerate(pitches):
                        if pitch.at_bat.id != current_ab:
                            current_ab = pitch.at_bat.id
                            last_pitches_array.append(video_array[i - 1])
                        elif i == len(pitches) - 1:
                            last_pitches_array.append(pitch_video)

                    video_array = last_pitches_array

                if len(video_array):
                    final_clip = concatenate_videoclips(video_array)
                    final_clip.write_videofile(
                        f'/Users/aadams/Downloads/plays/video-test_{options["atbat_ids"][0]}_v2.mp4', fps=59.94)
