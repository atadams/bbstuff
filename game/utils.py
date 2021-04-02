import sys
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
    if player.name_last == '':
        player.name_first = player.name_first_last.split(' ', 1)[0]
        player.name_last = player.name_first_last.split(' ', 1)[1]
        player.save()

    return player


def get_game(game_id, game_date, game_status, home_team, away_team, data):
    game, created = Game.objects.get_or_create(
        id=game_id,
        defaults={
            'date': game_date,
            # 'game_status': game_status,
            'home_team': home_team,
            'away_team': away_team,
        }
    )
    game.date = game_date
    game.data = data
    game.save()

    return game


def get_game_statsapi(game_id, game_date, game_status, home_team, away_team, data):
    game, created = Game.objects.get_or_create(
        id=game_id,
        defaults={
            'date': game_date,
            # 'game_status': game_status,
            'home_team': home_team,
            'away_team': away_team,
        }
    )
    game.date = game_date
    game.api_data = data
    game.save()

    return game


def get_ab(game, ab_dict, top_bottom):
    batter = get_player_by_id_name(ab_dict['batter'], ab_dict['batter_name'])
    pitcher = get_player_by_id_name(ab_dict['pitcher'], ab_dict['pitcher_name'])
    at_bat, created = AtBat.objects.get_or_create(
        game=game,
        ab_number=ab_dict['ab_number'],
        defaults={
            'top_bottom': top_bottom,
            'team_batting_id': ab_dict['team_batting_id'],
            'team_pitching_id': ab_dict['team_fielding_id'],
            'batter': batter,
            'pitcher': pitcher,
            'inning': ab_dict['inning'],
            'ab_number': ab_dict['ab_number'],
        }
    )
    at_bat.result = ab_dict.get('result', '')
    at_bat.description = ab_dict.get('des', '')
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


def even_number(num):
    int_num = int(num)
    if int_num % 2 == 0:
        return int_num
    else:
        return int_num + 1


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
