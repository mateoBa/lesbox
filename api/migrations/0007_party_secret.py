# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-02 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_track_android_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='secret',
            field=models.CharField(max_length=65, null='True'),
        ),
    ]