from decimal import Decimal

import matplotlib.pyplot as plt
import statsapi
from django.core.management import BaseCommand
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from pandas import np, qcut

from PyMLBStats.baseball import hotColdZones, vStrikeZoneData
from game import game_video
from game.graphics import attack_zones, inning_count_block, pitch_display_lg, player_name_block, strike_zone_block, \
    text_image
from game.models import Pitch, get_pitch_aggregates, get_pitches_by_at_bat_ids, get_pitches_by_ids
from natsgifbot.newmlbstats import get_pitch_arsenal, get_player_stats


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
        # meta = statsapi.meta('situationCodes')
        # meta2 = statsapi.meta('statGroups')
        # meta3 = statsapi.meta('statTypes')
        # arsenal = get_pitch_arsenal(425844)
        # print(meta)


        # options['atbat_ids'] = [2397]
        # options['atbat_ids'] = [2663]
        # options['atbat_ids'] = [2379]
        options['atbat_ids'] = [3366]
        options['show-pitch-data'] = True
        display_previous_velo = False
        display_attack_zones = False

        pitches = None
        if options['atbat_ids']:
            pitches = get_pitches_by_at_bat_ids(options['atbat_ids'])
        elif options['pitch_ids']:
            pitches = get_pitches_by_ids(options['pitch_ids'])

        if pitches:
            pitch_agg = get_pitch_aggregates(pitches.values_list('id', flat=True))
            previous_pitches = []
            pitches_zone = []

            if display_previous_velo:
                previous_velos = Pitch.objects.filter(at_bat__pitcher=pitches[0].at_bat.pitcher,
                                                      # at_bat__game=pitches[0].at_bat.game,
                                                      data__pitch_type=pitches[0].data['pitch_type'],
                                                      data__start_speed__lt=90).values_list('data__start_speed',
                                                                                            flat=True)

                n, bins, patches = plt.hist(previous_velos, density=False, bins=10)
                patches[8].set_fc('r')
                plt.show()

            attack_zones_clip = None

            if options['type'] == 'seq':
                video_array = []

                for i, pitch in enumerate(pitches):
                    scale = Decimal(pitch.zone_w) / pitch_agg['zone_w__max']
                    pitch_duration = 6 if i == len(pitches) - 1 else 2.75

                    pitch_video = game_video.get_pitch_video(
                        pitch,
                        crop_w=640,
                        prerelease_seconds=1.5,
                        duration=pitch_duration,
                        video_scale=scale,
                        crop_center_x=pitch.zone_center_x,
                        crop_center_y=pitch.zone_center_y,
                        adjust_x=70,
                        adjust_y=-80,
                    )

                    adjusted_zone_x = (pitch_video.w / 2) - (float(pitch.zone_w) / float(2) * float(scale)) + float(30)
                    adjusted_zone_y = (pitch_video.h / 2) - (float(pitch.zone_h) / float(2) * float(scale)) - float(80)

                    if options['show-pitch-data']:
                        count_image = inning_count_block(
                            inning=pitch.at_bat.inning,
                            top_bottom=pitch.at_bat.top_bottom,
                            balls=pitch.balls,
                            strikes=pitch.strikes,
                            outs=min(2, pitch.outs),
                            runners_str=pitch.runners_str,
                        )

                        count_clip = ImageClip(np.array(count_image)).set_duration(pitch_video.duration)

                        pitch_data_image = pitch_display_lg(
                            pitch.data['pitch_name'],
                            str(pitch.data['start_speed']),
                            outcome=pitch.pitch_result,
                            previous_pitches=previous_pitches,
                            width=count_clip.w - 15
                        )
                        pitch_data_clip = ImageClip(np.array(pitch_data_image)).set_duration(pitch_video.duration)

                        pitcher_name_image = player_name_block(
                            f'{pitch.at_bat.pitcher.name_last}',
                            logo_path=pitch.at_bat.team_pitching.team_logo_on_dark_path_png,
                            bg_color=pitch.at_bat.team_pitching.primary_color_hex,
                            width=10,
                        )
                        pitcher_name_clip = ImageClip(np.array(pitcher_name_image)).set_duration(pitch_video.duration)
                        pitcher_name_y = 10

                        vs_image = text_image('vs')
                        vs_clip = ImageClip(np.array(vs_image)).set_duration(pitch_video.duration)
                        vs_clip_x = pitcher_name_clip.w + 10

                        batter_name_image = player_name_block(
                            f'{pitch.at_bat.batter.name_last}',
                            logo_path=pitch.at_bat.team_batting.team_logo_on_dark_path_png,
                            bg_color=pitch.at_bat.team_batting.primary_color_hex,
                            width=10,
                        )
                        batter_name_clip = ImageClip(np.array(batter_name_image)).set_duration(pitch_video.duration)
                        batter_name_y = pitcher_name_y + pitcher_name_clip.h + 5

                        batter_name_x = vs_clip_x + vs_clip.w

                        count_y = batter_name_y + 10

                        pitch_data_y = count_y + count_clip.h + 10

                        pitches_zone.append([pitch.data['px'], pitch.data['pz'], pitch.data['call']])

                        if display_attack_zones:
                            batter_ba_zone_data = pitch.at_bat.batter.ba_dataframe(year='2020')
                            batter_ba_zone_data = batter_ba_zone_data.fillna(0)
                            data_bins = qcut(batter_ba_zone_data.ba, 20, labels=False, duplicates='drop')
                            data_colors = []
                            for cnt, idx in enumerate(data_bins, start=1):
                                data_colors.append(colors_array[idx])

                            # zone_colors = [
                            #     'rgb(6, 90, 238)',
                            #     'rgb(255, 255, 255)',
                            #     'rgb(214, 41, 52)',
                            #     'rgb(234, 147, 153)',
                            #     'rgb(6, 90, 238)',
                            #     'rgb(234, 147, 153)',
                            #     'rgb(6, 90, 238)',
                            #     'rgb(214, 41, 52)',
                            #     'rgb(255, 255, 255)',
                            #     'rgb(234, 147, 153)',
                            #     'rgb(6, 90, 238)',
                            #     'rgb(6, 90, 238)',
                            #     'rgb(150, 188, 255)',
                            #     'rgb(150, 188, 255)',
                            # ]
                            attack_zones_image = attack_zones(w=pitch.zone_w * 4, h=pitch.zone_h * 4, zones=data_colors)
                            # attack_zones_clip = ImageClip(np.array(attack_zones_image)).set_duration(
                            #     pitch_video.duration)

                        print(pitch.zone_w, pitch.zone_h, (pitch.data['sz_top'] - pitch.data['sz_bot']))

                        zone_image = strike_zone_block(
                            pitch.data['sz_top'],
                            pitch.data['sz_bot'],
                            pitch_array=pitches_zone,
                            # attack_zone_image=attack_zones_image,
                            # break_x=float(pitch.data["calc_break_x"]),
                            # break_z=float(pitch.data["calc_break_z_induced"]),
                        )
                        zone_clip = ImageClip(np.array(zone_image)).set_duration(pitch_video.duration)
                        zone_y = pitch_data_y + pitch_data_clip.h + 10

                        videos_array = [
                            pitch_video,
                            pitcher_name_clip.set_opacity(0.9).set_position((10, pitcher_name_y)),
                            vs_clip.set_opacity(0.9).set_position((vs_clip_x, pitcher_name_y)),
                            batter_name_clip.set_opacity(0.9).set_position((batter_name_x, pitcher_name_y)),
                            pitch_data_clip.set_opacity(0.9).set_position((10, pitch_data_y)),
                            # count_clip.set_opacity(0.9).set_position((, count_y)),
                            # attack_zones_clip.set_opacity(0.9).set_position(
                            #     (adjusted_zone_x - (attack_zones_clip.w * .125),
                            #      adjusted_zone_y - (attack_zones_clip.h * .125)
                            #      )),
                            # attack_zones_clip.set_opacity(0.9).set_position(
                            #     attack_zone_x_strike,
                            #     zone_y,
                            #     ),
                            zone_clip.set_opacity(0.9).set_position((10, zone_y)),
                        ]

                        if pitch.caption:
                            caption_image = text_image(pitch.caption, bg_color='#00000077', font_size=30)
                            zone_clip = ImageClip(np.array(caption_image)).set_duration(pitch_video.duration)
                            videos_array.append(zone_clip.set_position(('center', 0.9), relative=True))

                        pitch_video = CompositeVideoClip(videos_array)

                    video_array.append(pitch_video)
                    # previous_pitches.append([pitch.data['pitch_name'], str(pitch.data['start_speed'])])

                if len(video_array):
                    final_clip = concatenate_videoclips(video_array)
                    final_clip.write_videofile(
                        f'/Users/aadams/Downloads/plays/video-test_{options["atbat_ids"][0]}_v4.mp4', fps=59.94)
