import statsapi
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(statsapi.player_stats(next(
            x['id'] for x in statsapi.get('sports_players', {'season': 2019, 'gameType': 'W'})['people'] if
            x['fullName'] == 'Carlos Correa'), 'hitting,pitching,fielding', 'career'))
