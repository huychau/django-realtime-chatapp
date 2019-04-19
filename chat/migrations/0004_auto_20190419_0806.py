# Generated by Django 2.2 on 2019-04-19 08:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20190410_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='latest_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='room',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]