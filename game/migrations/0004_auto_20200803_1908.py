# Generated by Django 3.0.9 on 2020-08-04 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20200803_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='atbat',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='at_bat', to='game.Game'),
        ),
        migrations.AddField(
            model_name='atbat',
            name='top_bottom',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='atbat',
            name='batter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='batter', to='game.Player'),
        ),
        migrations.AlterField(
            model_name='atbat',
            name='pitcher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pitcher', to='game.Player'),
        ),
        migrations.AlterField(
            model_name='atbat',
            name='team_batting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_batting', to='game.Team'),
        ),
        migrations.AlterField(
            model_name='atbat',
            name='team_pitching',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_pitcher', to='game.Team'),
        ),
        migrations.CreateModel(
            name='Pitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.CharField(blank=True, db_index=True, max_length=10)),
                ('play_id', models.CharField(blank=True, db_index=True, max_length=40)),
                ('strikes', models.IntegerField(blank=True, null=True)),
                ('balls', models.IntegerField(blank=True, null=True)),
                ('pre_strikes', models.IntegerField(blank=True, null=True)),
                ('pre_balls', models.IntegerField(blank=True, null=True)),
                ('call', models.CharField(blank=True, max_length=10)),
                ('call_name', models.CharField(blank=True, max_length=10)),
                ('pitch_type', models.CharField(blank=True, max_length=10)),
                ('pitch_name', models.CharField(blank=True, max_length=10)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('balls_and_strikes', models.CharField(blank=True, max_length=10)),
                ('start_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('end_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('sz_top', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('sz_bot', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('extension', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('plateTime', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('zone', models.IntegerField(blank=True, null=True)),
                ('px', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('pz', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('x0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('y0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('z0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('ax', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('ay', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('az', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('vx0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('vy0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('vz0', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('calc_polynomial_y_1', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('back_yR', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('back_tR', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_x_3', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_y_3', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_z_3', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_x_2', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_y_2', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_z_2', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_x_1', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_polynomial_z_1', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_plate_time', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_plate_time_alt', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_end_time', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_break_x', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_break_z', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('calc_break_z_induced', models.DecimalField(blank=True, decimal_places=17, max_digits=20, null=True)),
                ('is_bip_out', models.BooleanField(default=False)),
                ('pitch_number', models.IntegerField(blank=True, null=True)),
                ('player_total_pitches', models.IntegerField(blank=True, null=True)),
                ('player_total_pitches_pitch_types', models.IntegerField(blank=True, null=True)),
                ('game_total_pitches', models.IntegerField(blank=True, null=True)),
                ('at_bat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.AtBat')),
            ],
        ),
    ]
