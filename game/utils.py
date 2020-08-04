from distutils.util import strtobool

from game.models import AtBat, Game, Pitch, Player, Team


def get_team_by_dict(team_dict):
    team, created = Team.objects.get_or_create(
        id=team_dict['id'],
        defaults={
            'team_code': team_dict['teamCode'],
            'file_code': team_dict['fileCode'],
            'club_common_name': team_dict['teamName'],
            'club_short_name': team_dict['shortName'],
            'location_name': team_dict['locationName'],
            'club_full_name': team_dict['name'],
            'abbreviation': team_dict['abbreviation'],
        }
    )

    return team


def get_player_by_id_name(player_id, player_name):
    player, created = Player.objects.get_or_create(
        id=player_id,
        defaults={
            'name_first_last': player_name,
        }
    )

    return player


def get_game(game_id, game_date, game_status, home_team, away_team, data):
    game, created = Game.objects.get_or_create(
        id=game_id,
        defaults={
            'date': game_date,
            'game_status': game_status,
            'home_team': home_team,
            'away_team': away_team,
        }
    )

    game.data = data
    game.save()

    return game


def get_ab(game, ab_dict, top_bottom):
    at_bat, created = AtBat.objects.get_or_create(
        game=game,
        ab_number=ab_dict['ab_number'],
        defaults={
            'top_bottom': top_bottom,
            'team_batting_id': ab_dict['team_batting_id'],
            'team_pitching_id': ab_dict['team_fielding_id'],
            'batter_id': ab_dict['batter'],
            'pitcher_id': ab_dict['pitcher'],
            'inning': ab_dict['inning'],
            'ab_number': ab_dict['ab_number'],
            'result': ab_dict['result'],
            'description': ab_dict['description'],
        }
    )
    at_bat.outcome_description = ab_dict['des']
    at_bat.save()

    return at_bat


def get_pitch(at_bat, pitch_dict):
    pitch, created = Pitch.objects.get_or_create(
        play_id=pitch_dict['play_id'],
        defaults={
            'row_id': pitch_dict['rowId'],
            'at_bat': at_bat,
        }
    )
    pitch.data = pitch_dict
    pitch.row_id = pitch_dict['rowId']
    pitch.save()

    return pitch
