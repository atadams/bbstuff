import os
from datetime import datetime

from django.db import models
from django.db.models import F, Max, Min

from config.settings.base import MEDIA_ROOT, PLAY_VIDEO_ROOT, PLAY_VIDEO_URL
from game.statcast import get_field_with_percentage, get_player_stats

LOGO_BASE_URL = f'https://www.mlbstatic.com/team-logos/'  # https://www.mlbstatic.com/team-logos/117.svg
LOGO_PATH_SVG = f'{MEDIA_ROOT}/team_logos/svg/'
LOGO_PATH_PNG = f'{MEDIA_ROOT}/team_logos/png/'
LOGO_ON_DARK_PATH_SVG = f'{MEDIA_ROOT}/team_logos_on_dark/svg/'
LOGO_ON_DARK_PATH_PNG = f'{MEDIA_ROOT}/team_logos_on_dark/png/'

BALL_ADJ = 1.5 / 12


class Team(models.Model):
    team_code = models.CharField(max_length=10, blank=True)  # teamCode
    file_code = models.CharField(max_length=10, blank=True)  # fileCode
    club_common_name = models.CharField(max_length=100, blank=True)  # teamName
    club_short_name = models.CharField(max_length=100, blank=True)  # ShortName
    club_full_name = models.CharField(max_length=100, blank=True)  # name
    location_name = models.CharField(max_length=100, blank=True)  # Locationname
    abbreviation = models.CharField(max_length=10, blank=True)  # abbreviation
    color_r = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    color_g = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    color_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    primary_color_hex = models.CharField(max_length=10, blank=True)
    secondary_color_hex = models.CharField(max_length=10, blank=True)
    tertiary_color_hex = models.CharField(max_length=10, blank=True)

    @property
    def team_logo_url_svg(self):
        return f'{LOGO_BASE_URL}team-cap-on-light/{self.id}.svg'

    @property
    def team_logo_on_dark_url_svg(self):
        return f'{LOGO_BASE_URL}team-cap-on-dark/{self.id}.svg'

    @property
    def team_logo_path_svg(self):
        return f'{LOGO_PATH_SVG}{self.id}.svg'

    @property
    def team_logo_path_png(self):
        return f'{LOGO_ON_DARK_PATH_PNG}{self.id}.png'

    @property
    def team_logo_on_dark_path_svg(self):
        return f'{LOGO_ON_DARK_PATH_SVG}{self.id}.svg'

    @property
    def team_logo_on_dark_path_png(self):
        return f'{LOGO_ON_DARK_PATH_PNG}{self.id}.png'


class Player(models.Model):
    name_first_last = models.CharField(max_length=50)  # "batter_name": "George Springer",
    name_first = models.CharField(max_length=50, blank=True)
    name_last = models.CharField(max_length=50, blank=True)

    @property
    def clean_name(self):
        player_name = self.name_first_last.lower().replace(" ", "-")
        player_name_clean = "".join(c for c in player_name.replace(" ", "-") if c.isalnum() or c == '-').rstrip()

        return player_name_clean

    @property
    def mugshot_url(self):
        return f'https://content.mlb.com/images/headshots/current/60x60/{self.id}.png'

    def ba_dataframe(self, player_type='batter', year='2020', p_throws='', pitch_type=''):
        return get_field_with_percentage(self.id, player_type=player_type, data_field='ba', year=year,
                                         p_throws=p_throws,
                                         pitch_type=pitch_type)

    @property
    def ba_zone_image(self, year='2020'):
        zone_data = self.ba_dataframe(year='2020')
        img = None

        return img

    @property
    def statsapi_data(self):
        return get_player_stats(self.id)

    @property
    def zone_top_bottom(self):
        data = self.statsapi_data

        return data['strikeZoneTop'], data['strikeZoneBottom']


class GameManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Game(models.Model):
    date = models.DateField()
    game_status = models.CharField(max_length=1, blank=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    is_active = models.BooleanField(default=True)

    data = models.JSONField(null=True)
    api_data = models.JSONField(null=True)

    objects = GameManager()

    def __str__(self):
        return self.game_description

    class Meta:
        ordering = ['-date']

    @property
    def game_description(self):
        return f'{self.away_team.club_common_name} @ {self.home_team.club_common_name} – {self.date.strftime("%m/%d/%Y")}'

    @property
    def game_description_full_date(self):
        return f'{self.away_team.club_common_name} @ {self.home_team.club_common_name} – {self.date.strftime("%B %d")}'

    @property
    def game_string(self):
        return f'{self.date.strftime("%Y%m%d")}_{self.away_team.file_code}-{self.home_team.file_code}'

    @property
    def path_name_with_id(self):
        return f'{self.game_string}_{self.id}'

    @property
    def is_previous_game(self):
        return datetime.today().date() > self.date

    @property
    def sheet_name(self):
        if self.away_team.abbreviation == 'HOU':
            home_away_string = f'@{self.home_team.abbreviation}'
        else:
            home_away_string = f'{self.away_team.abbreviation}'
        return f'{self.date.strftime("%-m-%-d")} {home_away_string}'


class AtBat(models.Model):
    inning = models.IntegerField()
    top_bottom = models.CharField(max_length=10, blank=True)
    ab_number = models.IntegerField()
    result = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='at_bats', null=True)
    team_batting = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_batting', null=True)
    team_pitching = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_pitcher', null=True)
    batter = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='batter', null=True)
    pitcher = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='pitcher', null=True)

    class Meta:
        ordering = ['ab_number', 'inning', '-top_bottom']

    @property
    def top_bottom_character(self):
        return 't' if self.top_bottom == 'Top' else 'b'

    @property
    def inning_number_string(self):
        return str(self.inning).zfill(2)

    @property
    def inning_string(self):
        return f'{self.top_bottom_character}{self.inning_number_string}'

    @property
    def full_inning_string(self):
        return f'{self.top_bottom} {self.inning}'

    @property
    def best_description(self):
        if self.description:
            return self.description

        return self.result


class Pitch(models.Model):
    row_id = models.CharField(max_length=10, blank=True, db_index=True)

    play_id = models.CharField(max_length=40, blank=True, db_index=True)

    data = models.JSONField(null=True)

    at_bat = models.ForeignKey(AtBat, on_delete=models.CASCADE, related_name='pitches')

    caption = models.CharField(max_length=400, blank=True)
    caption_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    video_rubber_x = models.IntegerField(default=427)
    video_rubber_y = models.IntegerField(default=430)
    pitcher_height_y = models.IntegerField(default=480)

    crop_top_left_x = models.DecimalField(max_digits=8, decimal_places=2, default=440.0)
    crop_top_left_y = models.DecimalField(max_digits=8, decimal_places=2, default=144.0)
    crop_bottom_right_x = models.DecimalField(max_digits=8, decimal_places=2, default=840.0)
    crop_bottom_right_y = models.DecimalField(max_digits=8, decimal_places=2, default=620.0)

    zone_top_left_x = models.DecimalField(max_digits=8, decimal_places=2, default=616.0)
    zone_top_left_y = models.DecimalField(max_digits=8, decimal_places=2, default=268.0)
    zone_bottom_right_x = models.DecimalField(max_digits=8, decimal_places=2, default=664.0)
    zone_bottom_right_y = models.DecimalField(max_digits=8, decimal_places=2, default=332.0)

    pitch_scene_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pitch_release_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pitch_plate_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    include_in_tipping = models.BooleanField(default=True)
    include_in_overlay = models.BooleanField(default=True)

    strike_probability = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.data["pitch_name"]} – {self.data["description"]}'

    class Meta:
        ordering = ['data__game_total_pitches']

    @property
    def balls(self):
        return self.data['balls']

    @property
    def strikes(self):
        return self.data['strikes']

    @property
    def outs(self):
        return self.data['outs']

    @property
    def next_pitch_id(self):
        try:
            pitch = Pitch.objects.get(at_bat__game__id=self.at_bat.game.id,
                                      data__game_total_pitches=self.data['game_total_pitches'] + 1)
        except Pitch.DoesNotExist:
            return self.id

        return pitch.id

    def video_filename(self, extension='mp4'):
        return f'{self.play_string}.{extension}'

    @property
    def crop_w(self):
        return self.crop_bottom_right_x - self.crop_top_left_x

    @property
    def crop_h(self):
        return self.crop_bottom_right_y - self.crop_top_left_y

    @property
    def zone_w(self):
        return self.zone_bottom_right_x - self.zone_top_left_x

    @property
    def zone_h(self):
        return self.zone_bottom_right_y - self.zone_top_left_y

    @property
    def zone_center_x(self):
        return int(self.zone_top_left_x + (self.zone_w / 2))

    @property
    def zone_center_y(self):
        return int(self.zone_top_left_y + (self.zone_h / 2))

    @property
    def video_filepath(self):
        return f'{PLAY_VIDEO_ROOT}{self.at_bat.game.path_name_with_id}/{self.video_filename()}'

    @property
    def scaled_video_filepath(self):
        return f'{MEDIA_ROOT}/scaled_plays/{self.at_bat.game.path_name_with_id}/{self.video_filename()}'

    @property
    def video_url(self):
        return f'{PLAY_VIDEO_URL}{self.at_bat.game.path_name_with_id}/{self.video_filename()}'

    @property
    def pitch_number(self):
        return self.data['pitch_number']

    @property
    def pitch_number_string(self):
        return str(self.data['pitch_number']).zfill(2)

    @property
    def play_string(self):
        return f'{self.at_bat.inning_string}_ab{self.at_bat.ab_number}_{self.at_bat.batter.clean_name}_p{self.pitch_number_string}'

    @property
    def play_string_with_id(self):
        return f'{self.play_string}_{self.play_id}'

    @property
    def pitch_result(self):
        return self.data['call_name']

    @property
    def ab_description(self):
        return self.data['des']

    @property
    def is_highlight(self):
        if 'team_batting' in self.data and self.data['team_batting'] == 'HOU':
            if self.data['call_name'] == 'In Play' and self.data.get('result', '') in ['Home Run', '2B', '3B', 'Triple',
                                                                                       'Double', 'Single']:
                return True

        if self.data['team_fielding'] == 'HOU':
            if self.data['strikes'] == 2 and self.data['call'] == 'S' and not self.data['description'] == 'Foul':
                return True

        return False

    @property
    def video_exists(self):
        return os.path.exists(self.video_filepath)

    def mlb_video_url(self, feed='home'):
        # return f'https://fastball-clips.mlb.com/{self.at_bat.game_id}/{feed}/{self.play_id}.mp4'
        return f'https://baseballsavant.mlb.com/sporty-videos?playId={self.play_id}'

    @property
    def mlb_video_url_home(self):
        return self.mlb_video_url(feed='home')

    @property
    def mlb_video_url_away(self):
        return self.mlb_video_url(feed='away')

    @property
    def mlb_video_url_network(self):
        return self.mlb_video_url(feed='network')

    @property
    def mlb_video_url_astros(self):
        if self.at_bat.game.home_team.club_common_name == 'Astros':
            return self.mlb_video_url_home
        else:
            return self.mlb_video_url_away

    @property
    def zone_coordinates(self):
        return (self.crop_top_left_x, self.crop_top_left_x), (self.crop_bottom_right_x, self.crop_bottom_right_y)

    @property
    def runner_1_str(self):
        return 1 if 'runnerOn1B' in self.data else 0

    @property
    def runner_2_str(self):
        return 2 if 'runnerOn2B' in self.data else 0

    @property
    def runner_3_str(self):
        return 3 if 'runnerOn3B' in self.data else 0

    @property
    def runners_str(self):
        return f'{self.runner_1_str}{self.runner_2_str}{self.runner_3_str}'

    @property
    def runners_icon_filepath(self):
        return f'{MEDIA_ROOT}icons/runners-{self.runners_str}.png'

    @property
    def in_zone(self):
        if (abs(self.data['px']) <= 20 / 2 / 12) and (self.data['sz_bot'] - BALL_ADJ) <= self.data['pz'] <= (
            self.data['sz_top'] + BALL_ADJ):
            return True
        else:
            return False

    @property
    def in_standard_zone(self):
        if (abs(self.data['px']) <= 20 / 2 / 12) and (1.5 - BALL_ADJ) <= self.data['pz'] <= (3.5 + BALL_ADJ):
            return True
        else:
            return False


def get_pitches_by_at_bat_ids(at_bat_ids, only_marked_include=True):
    return Pitch.objects.filter(at_bat_id__in=at_bat_ids, include_in_tipping=only_marked_include).order_by(
        'at_bat__game__date', 'data__game_total_pitches')


def get_pitches_by_ids(pitch_ids, only_marked_include=True):
    return Pitch.objects.filter(id__in=pitch_ids, include_in_tipping=only_marked_include).order_by(
        'at_bat__game__date', 'data__game_total_pitches')


def get_pitch_aggregates(pitch_ids):
    pitches_agg = Pitch.objects.filter(id__in=pitch_ids).annotate(
        duration=F('pitch_release_time') - F('pitch_scene_time'),
        zone_w=F('zone_bottom_right_x') - F('zone_top_left_x'),
        zone_h=F('zone_bottom_right_y') - F('zone_top_left_y'),
        crop_w=F('crop_bottom_right_x') - F('crop_top_left_x'),
        crop_h=F('crop_bottom_right_y') - F('crop_top_left_y'),
    )

    return pitches_agg.aggregate(
        Min('zone_w'),
        Max('zone_w'),
        Min('zone_h'),
        Max('zone_h'),
        Min('crop_w'),
        Max('crop_w'),
        Min('crop_h'),
        Max('crop_h'),
        Min('pitcher_height_y'),
        Max('pitcher_height_y'),
        Max('pitch_scene_time'),
        Max('pitch_release_time'),
        Min('duration'),
        Max('duration'),
    )
