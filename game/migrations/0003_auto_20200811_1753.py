# Generated by Django 3.1 on 2020-08-11 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_game_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='color_b',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
        migrations.AddField(
            model_name='team',
            name='color_g',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
        migrations.AddField(
            model_name='team',
            name='color_r',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
    ]