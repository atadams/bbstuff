import cairosvg
import mlbgame
import requests
from django.core.management import BaseCommand

from game.models import Team

# 'team_code': team_dict['teamCode'],
# 'file_code': team_dict['fileCode'],
# 'club_common_name': team_dict['teamName'],
# 'club_short_name': team_dict['shortName'],
# 'location_name': team_dict['locationName'],
# 'club_full_name': team_dict['name'],
# 'abbreviation': team_dict['abbreviation'],


class Command(BaseCommand):
    def handle(self, *args, **options):
        import_logos = True
        teams = mlbgame.teams()

        for team in teams:
            color = team.primary if team.primary != '#000000' else team.secondary
            h = color.lstrip('#')
            r, g, b = tuple(float(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
            # print('RGB =', tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)))
            print("{0:.1f}".format(r), "{0:.2f}".format(g), "{0:.2f}".format(b))
            obj, created = Team.objects.update_or_create(
                id=team.team_id,
                defaults={
                    'team_code': team.team_code,
                    # 'club': team.club,
                    'club_common_name': team.club_common_name,
                    'club_full_name': team.club_full_name,
                    # 'name_display_long': team.name_display_long,
                    'club_short_name': team.name_display_short,
                    'file_code': team.display_code,
                    'location_name': team.city,
                    'abbreviation': team.display_code.upper(),
                    'color_r': "{0: .1f}".format(r),
                    'color_g': "{0: .1f}".format(g),
                    'color_b': "{0: .1f}".format(b),
                    # 'venue_id': team.venue_id,
                    # 'field': team.field,
                    # 'league': team.league,
                    # 'location': team.location,
                    # 'timezone': team.timezone,
                    # 'aws_club_slug': team.aws_club_slug,
                    # 'youtube': team.youtube,
                }
            )
            obj.primary_color_hex = team.primary
            obj.secondary_color_hex = team.secondary
            obj.tertiary_color_hex = team.tertiary
            obj.save()

            if import_logos:
                myfile = requests.get(obj.team_logo_url_svg)
                if myfile.ok:
                    open(obj.team_logo_path_svg, 'wb').write(myfile.content)

                    cairosvg.svg2png(
                        file_obj=open(obj.team_logo_path_svg, "rb"),
                        write_to=obj.team_logo_path_png,
                        scale=3,
                    )

                myfile = requests.get(obj.team_logo_on_dark_url_svg)
                print(obj.team_logo_on_dark_url_svg, obj.team_logo_on_dark_path_png)
                if myfile.ok:
                    open(obj.team_logo_on_dark_path_svg, 'wb').write(myfile.content)

                    cairosvg.svg2png(
                        file_obj=open(obj.team_logo_on_dark_path_svg, "rb"),
                        write_to=obj.team_logo_on_dark_path_png,
                        scale=3,
                    )
