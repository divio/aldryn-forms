# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-18 12:49
from __future__ import unicode_literals

from django.db import migrations, models

import aldryn_forms.utils


action_backends_choices = aldryn_forms.utils.action_backend_choices()
action_backends_choices = [(choice[0], str(choice[1])) for choice in action_backends_choices]


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0008_auto_20170316_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='formplugin',
            name='storage_backend',
            field=models.CharField(choices=action_backends_choices, default='default', max_length=15, verbose_name='Action backend'),
        ),
    ]
