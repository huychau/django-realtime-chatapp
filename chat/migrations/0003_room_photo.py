# Generated by Django 2.2 on 2019-04-23 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20190423_0340'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='photo',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
