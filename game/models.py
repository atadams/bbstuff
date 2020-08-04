from django.db import models

from config.settings.base import MEDIA_URL, PLAY_VIDEO_ROOT, PLAY_VIDEO_URL


class Team(models.Model):
    team_code = models.CharField(max_length=10, blank=True)  # teamCode
    file_code = models.CharField(max_length=10, blank=True)  # fileCode
    club_common_name = models.CharField(max_length=100, blank=True)  # teamName
    club_short_name = models.CharField(max_length=100, blank=True)  # ShortName
    club_full_name = models.CharField(max_length=100, blank=True)  # name
    location_name = models.CharField(max_length=100, blank=True)  # Locationname
    abbreviation = models.CharField(max_length=10, blank=True)  # abbreviation


class Player(models.Model):
    name_first_last = models.CharField(max_length=50)  # "batter_name": "George Springer",

    @property
    def clean_name(self):
        player_name = self.name_first_last.lower().replace(" ", "-")
        player_name_clean = "".join(c for c in player_name.replace(" ", "-") if c.isalnum() or c == '-').rstrip()

        return player_name_clean


class Game(models.Model):
    date = models.DateField()
    game_status = models.CharField(max_length=1, blank=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')

    data = models.JSONField(null=True)

    def __str__(self):
        return self.game_description

    class Meta:
        ordering = ['-date']

    @property
    def game_description(self):
        return f'{self.away_team.club_common_name} @ {self.home_team.club_common_name} – {self.date.strftime("%m/%d/%Y")}'

    @property
    def game_string(self):
        return f'{self.date.strftime("%Y%m%d")}_{self.away_team.file_code}-{self.home_team.file_code}'

    @property
    def path_name_with_id(self):
        return f'{self.game_string}_{self.id}'


class AtBat(models.Model):
    inning = models.IntegerField()
    top_bottom = models.CharField(max_length=10, blank=True)
    ab_number = models.IntegerField()
    result = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=300, blank=True)
    outcome_description = models.CharField(max_length=300, blank=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='at_bats', null=True)
    team_batting = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_batting', null=True)
    team_pitching = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_pitcher', null=True)
    batter = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='batter', null=True)
    pitcher = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='pitcher', null=True)

    class Meta:
        ordering = ['inning', '-top_bottom']

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


class Pitch(models.Model):
    row_id = models.CharField(max_length=10, blank=True, db_index=True)

    play_id = models.CharField(max_length=40, blank=True, db_index=True)

    data = models.JSONField(null=True)

    at_bat = models.ForeignKey(AtBat, on_delete=models.CASCADE, related_name='pitches')

    video_rubber_x = models.IntegerField(default=427)
    video_rubber_y = models.IntegerField(default=430)
    pitcher_height_y = models.IntegerField(default=480)

    pitch_scene_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pitch_release_time = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return f'{self.data["pitch_name"]} – {self.data["description"]}'

    class Meta:
        ordering = ['data__game_total_pitches']

    @property
    def next_pitch_id(self):
        try:
            pitch = Pitch.objects.get(data__game_total_pitches=self.data['game_total_pitches'] + 1)
        except Pitch.DoesNotExist:
            pitch = None

        return pitch.id

    def video_filename(self, extension='mp4'):
        return f'{self.at_bat.game.game_string}_{self.play_string}.{extension}'

    @property
    def video_filepath(self):
        return f'{PLAY_VIDEO_ROOT}{self.at_bat.game.path_name_with_id}/{self.video_filename()}'

    @property
    def video_url(self):
        return f'{PLAY_VIDEO_URL}{self.at_bat.game.path_name_with_id}/{self.video_filename()}'


    @property
    def pitch_number_string(self):
        return str(self.data['pitch_number']).zfill(2)

    @property
    def play_string(self):
        return f'ab{self.at_bat.ab_number}_{self.at_bat.batter.clean_name}_p{self.pitch_number_string}'

    @property
    def play_string_with_id(self):
        return f'{self.play_string}_{self.play_id}'
