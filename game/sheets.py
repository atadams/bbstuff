from django_pandas.io import read_frame
from googleapiclient.discovery import build
# If modifying these scopes, delete the file token.pickle.
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame

from config.settings.base import APPS_DIR
from game.models import Game, Pitch

SCOPES = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive',
          ]

# The ID and range of a sample spreadsheet.
ASTROS_SPREADSHEET_ID = '1cHSxS7YT8uSgIzAIzAS4bF6E2FvKasTF6QW4FyrOsB4'

creds = ServiceAccountCredentials.from_json_keyfile_name(f'{APPS_DIR}/creds.json', SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()


def add_sheet(sheet_name, r=0.00, g=0.20, b=0.40):
    sheet_metadata = sheet.get(spreadsheetId=ASTROS_SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    game_sheet = None
    for this_sheet in sheets:
        if this_sheet.get("properties", {}).get("title", sheet_name) == sheet_name:
            return this_sheet

    try:
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'tabColor': {
                            'red': str(r),
                            'green': str(g),
                            'blue': str(b)
                        }
                    }
                }
            }]
        }

        response = sheet.batchUpdate(
            spreadsheetId=ASTROS_SPREADSHEET_ID,
            body=request_body
        ).execute()

        return response
    except Exception as e:
        print(e)


def add_game(game_id):
    game = Game.objects.get(pk=game_id)

    if game.away_team.abbreviation == 'HOU':
        opponent = game.home_team
    else:
        opponent = game.away_team

    game_sheet = add_sheet(game.sheet_name, opponent.color_r, opponent.color_g, opponent.color_b)

    pitches = Pitch.objects.filter(at_bat__game=game)
    pitch_data = []
    for pitch in pitches:
        current_pitch = {
            'inning': pitch.at_bat.inning,
            'top_bottom': pitch.at_bat.top_bottom,
            'ab_number': pitch.at_bat.ab_number,
            'play_id': pitch.play_id,
        }
        pitch_data.append(current_pitch)
    df = DataFrame(pitch_data)
    my_list = [['2018-11-10', '1000000000', '14003', '140', '576.1786404'],
               ['2018-11-11', '506541', '14067', '357', '578.8120356'],
               ['2018-11-12', '423175', '15250', '330', '627.4887'],
               ['2018-11-13', '274503', '11337', '240', '466.4812716'],
               ['2018-11-14', '285468', '11521', '194', '474.0522828']]

