# Generated by Django 3.1 on 2020-08-29 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_auto_20200825_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='primary_color_hex',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='team',
            name='secondary_color_hex',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='team',
            name='tertiary_color_hex',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
