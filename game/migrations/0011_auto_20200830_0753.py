# Generated by Django 3.1 on 2020-08-30 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20200828_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='name_first',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='player',
            name='name_last',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
