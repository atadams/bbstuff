# Generated by Django 3.1 on 2020-08-25 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20200821_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='pitch',
            name='pitch_plate_time',
            field=models.DecimalField(decimal_places=2, default=3.0, max_digits=8),
        ),
    ]
