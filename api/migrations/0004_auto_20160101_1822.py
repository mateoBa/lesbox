# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-01 18:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20151231_1818'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='lastTokenSpotify',
            new_name='last_token_spotify',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='spotifyId',
            new_name='spotify_id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='userName',
            new_name='user_name',
        ),
    ]
