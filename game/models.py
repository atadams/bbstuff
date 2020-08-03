from django.db import models


class Team(models.Model):
    team_code = models.CharField(max_length=10, blank=True)  # teamCode
    file_code = models.CharField(max_length=10, blank=True)  # fileCode
    club_common_name = models.CharField(max_length=100, blank=True)  # teamName
    club_full_name = models.CharField(max_length=100, blank=True)  # name
    abbreviation = models.CharField(max_length=10, blank=True)  # abbreviation
