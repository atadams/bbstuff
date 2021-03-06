# Generated by Django 3.1 on 2020-08-06 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtBat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inning', models.IntegerField()),
                ('top_bottom', models.CharField(blank=True, max_length=10)),
                ('ab_number', models.IntegerField()),
                ('result', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=300)),
            ],
            options={
                'ordering': ['ab_number', 'inning', '-top_bottom'],
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_first_last', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_code', models.CharField(blank=True, max_length=10)),
                ('file_code', models.CharField(blank=True, max_length=10)),
                ('club_common_name', models.CharField(blank=True, max_length=100)),
                ('club_short_name', models.CharField(blank=True, max_length=100)),
                ('club_full_name', models.CharField(blank=True, max_length=100)),
                ('location_name', models.CharField(blank=True, max_length=100)),
                ('abbreviation', models.CharField(blank=True, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Pitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.CharField(blank=True, db_index=True, max_length=10)),
                ('play_id', models.CharField(blank=True, db_index=True, max_length=40)),
                ('data', models.JSONField(null=True)),
                ('video_rubber_x', models.IntegerField(default=427)),
                ('video_rubber_y', models.IntegerField(default=430)),
                ('pitcher_height_y', models.IntegerField(default=480)),
                ('pitch_scene_time', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('pitch_release_time', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('at_bat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pitches', to='game.atbat')),
            ],
            options={
                'ordering': ['data__game_total_pitches'],
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('game_status', models.CharField(blank=True, max_length=1)),
                ('data', models.JSONField(null=True)),
                ('away_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='game.team')),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='game.team')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='atbat',
            name='batter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batter', to='game.player'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='at_bats', to='game.game'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='pitcher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pitcher', to='game.player'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='team_batting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_batting', to='game.team'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='team_pitching',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_pitcher', to='game.team'),
        ),
    ]
