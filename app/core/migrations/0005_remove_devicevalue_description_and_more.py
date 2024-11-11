# Generated by Django 5.1.2 on 2024-11-11 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_iot_device_devicevalue_device'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devicevalue',
            name='description',
        ),
        migrations.AddField(
            model_name='devicevalue',
            name='bigvehicle_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='devicevalue',
            name='car_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='devicevalue',
            name='motorcycle_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='devicevalue',
            name='smalltruck_count',
            field=models.IntegerField(default=0),
        ),
    ]
