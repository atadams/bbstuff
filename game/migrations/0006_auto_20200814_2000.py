# Generated by Django 3.1 on 2020-08-15 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20200814_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pitch',
            name='crop_bottom_right_y',
            field=models.DecimalField(decimal_places=2, default=620.0, max_digits=8),
        ),
    ]
