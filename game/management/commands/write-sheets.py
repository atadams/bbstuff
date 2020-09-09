from django.core.management import BaseCommand
from django.db.models import Q

from game.models import Game
from game.sheets import add_game, add_sheet


class Command(BaseCommand):
    def handle(self, *args, **options):
        games = Game.objects.filter(Q(away_team__abbreviation='HOU') | Q(home_team__abbreviation='HOU'))

        for game in games:
            print(game.sheet_name)

            if game.away_team.abbreviation == 'HOU':
                opponent = game.home_team
            else:
                opponent = game.away_team

            sheet = add_game(game.id)
