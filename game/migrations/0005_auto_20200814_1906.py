# Generated by Django 3.1 on 2020-08-15 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20200812_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='pitch',
            name='crop_bottom_right_x',
            field=models.DecimalField(decimal_places=2, default=840.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='crop_bottom_right_y',
            field=models.DecimalField(decimal_places=2, default=332.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='crop_top_left_x',
            field=models.DecimalField(decimal_places=2, default=440.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='crop_top_left_y',
            field=models.DecimalField(decimal_places=2, default=144.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='zone_bottom_right_x',
            field=models.DecimalField(decimal_places=2, default=664.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='zone_bottom_right_y',
            field=models.DecimalField(decimal_places=2, default=332.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='zone_top_left_x',
            field=models.DecimalField(decimal_places=2, default=616.0, max_digits=8),
        ),
        migrations.AddField(
            model_name='pitch',
            name='zone_top_left_y',
            field=models.DecimalField(decimal_places=2, default=268.0, max_digits=8),
        ),
    ]
