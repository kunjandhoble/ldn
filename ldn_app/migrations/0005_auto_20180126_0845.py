# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-26 03:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ldn_app', '0004_auto_20171228_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypaltransaction',
            name='subscription_end_date',
            field=models.DateTimeField(default=datetime.datetime(2019, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='paypaltransaction',
            name='transaction_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 26, 8, 45, 12, 151000)),
        ),
    ]
