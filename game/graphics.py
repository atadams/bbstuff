import math

from PIL import Image, ImageDraw, ImageFont, ImageOps
# font_path = '/Users/aadams/Downloads/fonts/Roboto_v2.0/RobotoCondensed-Bold.ttf'
from PIL.Image import LANCZOS
from PIL.ImageOps import mirror

from config.settings.base import MEDIA_ROOT
from game.constants import PITCH_COLORS, PITCH_COLORS_LIGHT

font_path = '/Users/aadams/Downloads/fonts/OpenSans/OpenSans-CondBold.ttf'


def pitch_display_lg(pitch_type='', pitch_velo=0.0, outcome='', previous_pitches=[], width=0):
    text_pitch = pitch_type
    text_label = u'VELOCITY'
    text_speed = f'{pitch_velo:.1f}'
    text_mph = u'MPH'
    font_lg = ImageFont.truetype(font_path, 34)
    font_md = ImageFont.truetype(font_path, 14)
    font_sm = ImageFont.truetype(font_path, 12)

    outcome = outcome.upper()
    # Get the line sizes
    text_pitch_w, text_pitch_h = font_md.getsize(text_pitch.upper())
    text_outcome_w, text_outcome_h = font_md.getsize(outcome)
    text_speed_w, text_speed_h = font_lg.getsize(text_speed, features=['pnum'])
    text_mph_w, text_mph_h = font_sm.getsize(text_mph)

    prev_all_h = 0
    prev_all_w_max = 0

    if len(previous_pitches):
        for i, previous_pitch in enumerate(previous_pitches):
            prev_text_pitch = f'{previous_pitch[1]} MPH {previous_pitch[0]}'
            text_pitch_w, text_pitch_h = font_sm.getsize(prev_text_pitch)
            prev_all_h += text_pitch_h + 5
            prev_all_w_max = max(prev_all_w_max, text_speed_w)
            previous_pitches[i].append(prev_text_pitch)
            previous_pitches[i].append(text_pitch_h)

    main_image_w = max(width, text_pitch_w + 15, text_speed_w + text_mph_w + 2 + 15)

    canvas = Image.new(
        'RGB',
        (
            main_image_w,
            prev_all_h + text_pitch_h + text_speed_h + text_outcome_h + 15
        ),
        "white"
    )

    # Draw the text onto the text canvas, and use black as the text color
    draw = ImageDraw.Draw(canvas)
    current_y = 0
    for previous_pitch in previous_pitches:
        draw.text((10, current_y), previous_pitch[2], 'gray', font_sm)
        current_y += previous_pitch[3] + 5

    current_y += 0

    draw.text((int((main_image_w - text_speed_w) / 2), current_y), text_speed, 'black', font_lg,
              features=['pnum', 'dlig'])
    current_y += text_speed_h

    # draw.text((text_speed_w + 15, current_y - text_mph_h), text_mph, 'gray', font_sm)
    current_y += 5

    draw.text((int((main_image_w - text_pitch_w) / 2), current_y), text_pitch.upper(), 'black', font_md)
    current_y += text_pitch_h + 10

    if outcome:
        draw.text(((main_image_w - text_outcome_w) / 2, current_y), outcome, 'black', font_md)

    # canvas.show()

    return canvas


def pitch_display_sm(pitch_type='', pitch_velo='', width=None):
    text_pitch = f'{pitch_velo} mph {pitch_type}'
    font_sm = ImageFont.truetype(font_path, 16)

    text_pitch_w, text_pitch_h = font_sm.getsize(text_pitch)
    image_w = (text_pitch_w + 10) if width is not None else width

    # create a blank canvas with extra space between lines
    canvas = Image.new(
        'RGB',
        (
            image_w,
            text_pitch_h + 10,
        ),
        "white"
    )

    # Draw the text onto the text canvas, and use black as the text color
    draw = ImageDraw.Draw(canvas)

    draw.text((5, 5), text_pitch, 'black', font_sm)

    return canvas


def player_name_block(player_name, logo_path='', bg_color='black', width=None):
    font_md = ImageFont.truetype(font_path, 20)

    ascent, descent = font_md.getmetrics()

    font_height = ascent + descent

    text_name_w, text_name_h = font_md.getsize(player_name)

    logo_width = 0
    logo_image = None
    if logo_path:
        logo_image = Image.open(logo_path)
        logo_image = ImageOps.scale(logo_image, (ascent - 6) / logo_image.height)
        logo_width = logo_image.width + 10

    canvas_width = max(width, logo_width + text_name_w + 20)

    canvas = Image.new(
        'RGB',
        (
            canvas_width,
            font_height + 5,
        ),
        bg_color,
    )

    if logo_image:
        canvas.paste(logo_image, (10, int(math.floor((canvas.height - logo_image.height) / 2))), logo_image)

    draw = ImageDraw.Draw(canvas)

    draw.text((logo_width + 10, 0), player_name, 'white', font_md)

    # canvas.show()

    return canvas


def inning_count_block(inning=1, top_bottom='t', balls=0, strikes=0, outs=0, runners_str='000'):
    font_md = ImageFont.truetype(font_path, 20)
    count = f'{str(balls)}-{str(strikes)}'

    outs_image = Image.open(f'{MEDIA_ROOT}/icons/outs-{outs}.png')
    runners_image = Image.open(f'{MEDIA_ROOT}/icons/runners-{runners_str}.png')

    count_name_w, count_name_h = font_md.getsize(count)

    ascent, descent = font_md.getmetrics()
    (width, baseline), (offset_x, offset_y) = font_md.font.getsize(count)

    image_height = max(outs_image.height, runners_image.height, count_name_h) + 4

    canvas = Image.new(
        'RGB',
        (
            5 + count_name_w + 20 + outs_image.width + 20 + runners_image.width + 5,
            image_height,
        ),
        'black',
    )

    canvas.paste(outs_image, (count_name_w + 25, int((image_height - outs_image.height) / 2)), outs_image)
    canvas.paste(runners_image, (count_name_w + outs_image.width + 40, 2), runners_image)

    draw = ImageDraw.Draw(canvas)

    draw.text((10, 0), count, 'white', font_md)

    return canvas


def strike_zone_block(sz_top=3.5, sz_bottom=1.5, pitch_array=None, final_width=118, break_x=None, break_z=None,
                      show_plate=True, attack_zone_image=None, call='', attack_zones_data=None):
    if attack_zones_data is None:
        attack_zones_data = []
    if pitch_array is None:
        pitch_array = []
    pixels_per_inch = int(300 / 17)
    bottom_y = 1000
    center_x = 450
    scale = int(900 / final_width)
    call = call.upper()

    # width = width * 4
    zone_left_x = center_x - int(20 / 2 * pixels_per_inch)
    zone_right_x = center_x + int(20 / 2 * pixels_per_inch)
    zone_top = bottom_y - (int(sz_top * 12) * pixels_per_inch)
    zone_bottom = bottom_y - (int(sz_bottom * 12) * pixels_per_inch)

    strike_canvas = Image.new(
        'RGBA',
        (900, 1050,),
        'white',
    )

    draw = ImageDraw.Draw(strike_canvas)

    if len(attack_zones_data) == 13:
        outer_zone_order = [12, 11, 14, 13]
        inner_zone_order = [3, 2, 1, 6, 5, 4, 9, 8, 7]
        zone_third_w = int((zone_right_x - zone_left_x) / 3)
        zone_third_h = int((zone_bottom - zone_top) / 3)

        outer_w = zone_third_w * 2
        outer_h = zone_third_h * 2

        current_x = zone_left_x - int(zone_third_w / 2)
        current_y = zone_top - int(zone_third_h / 2)

        for i, azone in enumerate(outer_zone_order):
            draw.rectangle(
                [current_x, current_y, current_x + outer_w, current_y + outer_h],
                fill=attack_zones_data[azone - 2],
                outline=None,
                width=0,
            )
            current_x += outer_w
            if (i + 1) % 2 == 0:
                current_x = zone_left_x - int(zone_third_w / 2)
                current_y += outer_h

        current_x = zone_left_x
        current_y = zone_top

        for i, azone in enumerate(inner_zone_order):
            draw.rectangle(
                [current_x, current_y, current_x + zone_third_w, current_y + zone_third_h],
                fill=attack_zones_data[azone - 1],
                outline='#000000',
                width=1,
            )
            current_x += zone_third_w
            if (i + 1) % 3 == 0:
                current_x = zone_left_x
                current_y += zone_third_h
            # current_y = int(int((i + 1) / 3) * float(zone_third_h)) + zone_top

    if call:
        font = ImageFont.truetype(font_path, 16 * scale)
        text_pitch_w, text_pitch_h = font.getsize(call)
        draw.text(((900 - text_pitch_w) / 2, 10), call, 'black', font)

    if attack_zone_image:
        strike_canvas.paste(attack_zone_image, (int(center_x - (attack_zone_image.width / 2)), int(zone_top - (
            attack_zone_image.height * (1 / 8)))))

    draw.rectangle([zone_left_x, zone_top, zone_right_x, zone_bottom], outline='#FFFFFF', width=6)

    if show_plate:
        draw.polygon(
            [zone_left_x, 1000, zone_right_x,
             1000, zone_right_x, 975,
             center_x, 950,
             zone_left_x, 975],
            outline='#000000',
        )

    for index, pitch in enumerate(pitch_array, start=1):
        pitch_dot_size = 70
        pitch_dot_adjust = int(pitch_dot_size / 2)
        pitch_x = center_x - (int(pitch[0] * pixels_per_inch * 12)) - pitch_dot_adjust
        pitch_y = bottom_y - (int(pitch[1] * pixels_per_inch * 12)) - pitch_dot_adjust

        dot_outline = None

        if len(pitch) == 4:
            dot_fill = pitch[3]
        else:
            dot_fill = False

        if index == len(pitch_array):
            if not dot_fill:
                dot_fill = PITCH_COLORS[pitch[2]]
                dot_outline = 'black'
            if break_x and break_z:
                line_x = pitch_x + int(break_x * pixels_per_inch * 12) + pitch_dot_adjust
                line_y = pitch_y + int(break_z * pixels_per_inch * 12) + pitch_dot_adjust
                draw.line([line_x, line_y, pitch_x + pitch_dot_adjust, pitch_y + pitch_dot_adjust], fill='black',
                          width=1)
        else:
            if not dot_fill:
                dot_fill = PITCH_COLORS_LIGHT[pitch[2]]
                dot_outline = '#666666'

        draw.ellipse(
            [pitch_x, pitch_y, pitch_x + pitch_dot_size, pitch_y + pitch_dot_size],
            fill=dot_fill,
            outline=dot_outline,
            width=1,
        )

    draw.rectangle([zone_left_x, zone_top, zone_right_x, zone_bottom], fill=None, outline='#000000', width=2)

    strike_canvas = ImageOps.scale(strike_canvas, final_width / 900, resample=LANCZOS)

    # strike_canvas.show()

    return strike_canvas


def text_image(text='', text_color='white', bg_color='black', font_size=16, height=None):
    font_obj = ImageFont.truetype(font_path, font_size)

    text_w, text_h = font_obj.getsize(text)

    image_h = height if height else text_h + 10

    canvas = Image.new(
        'RGBA',
        (
            text_w + 10,
            image_h,
        ),
        bg_color,
    )

    draw = ImageDraw.Draw(canvas)
    draw.text((5, int(math.floor((image_h - text_h) / 2)) - 3), text, text_color, font_obj)

    return canvas


def attack_zones(w=100, h=150, zones=[]):
    zone_w = w / 3
    zone_h = h / 3

    canvas = Image.new(
        'RGBA',
        (w + zone_w, h + zone_h,),
        'white',
    )

    draw = ImageDraw.Draw(canvas)

    current_x = zone_w / 2
    current_y = zone_h / 2

    draw.rectangle([current_x, current_y, w, h], fill=None, outline='#AAAAAA', width=2)

    # print(w, h, zone_w, zone_h)

    draw.rectangle([0, 0, zone_w * 2, zone_h * 2], fill=zones[9], outline=None, width=0, )
    draw.rectangle([zone_w * 2, 0, zone_w * 4, zone_h * 2], fill=zones[10], outline=None, width=0, )
    draw.rectangle([0, zone_h * 2, zone_w * 2, zone_h * 4], fill=zones[11], outline=None, width=0, )
    draw.rectangle([zone_w * 2, zone_h * 2, zone_w * 4, zone_h * 4], fill=zones[12], outline=None, width=0, )

    for i, zone in enumerate(zones[0:9]):
        draw.rectangle(
            [current_x, current_y, current_x + zone_w, current_y + zone_h],
            fill=zone,
            outline=None,
            width=0,
        )
        # print(i, [current_x, current_y, current_x + zone_w, current_y + zone_h], zone)
        current_x += zone_w
        if (i + 1) % 3 == 0:
            current_x = zone_w / 2
        current_y = int(int((i + 1) / 3) * float(zone_h)) + zone_h / 2

    # canvas.show()

    return mirror(canvas)


def matchup_block(player_1, team_1, player_2, team_2):
    player_1_image = player_name_block(
        f'{player_1.name_last}',
        logo_path=team_1.team_logo_on_dark_path_png,
        bg_color=team_1.primary_color_hex,
        width=10,
    )

    vs_image = text_image('VS', height=player_1_image.height)

    player_2_image = player_name_block(
        f'{player_2.name_last}',
        logo_path=team_2.team_logo_on_dark_path_png,
        bg_color=team_2.primary_color_hex,
        width=10,
    )

    canvas = Image.new(
        'RGB',
        (
            player_1_image.width + vs_image.width + player_2_image.width,
            player_1_image.height,
        ),
        'black',
    )

    canvas.paste(player_1_image, (0, 0))
    canvas.paste(vs_image, (player_1_image.width, 0))
    canvas.paste(player_2_image, (player_1_image.width + vs_image.width, 0))

    return canvas
