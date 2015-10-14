# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Max value', validators=[django.core.validators.MaxLengthValidator(255)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Max value', validators=[django.core.validators.MaxLengthValidator(255)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Max value', validators=[django.core.validators.MaxLengthValidator(255)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formdata',
            name='language',
            field=models.CharField(default=b'en', max_length=10, verbose_name='language', choices=[(b'en', b'en'), (b'fr', b'fr'), (b'de', b'de')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Max value', validators=[django.core.validators.MaxLengthValidator(255)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Max value', validators=[django.core.validators.MaxLengthValidator(255)]),
            preserve_default=True,
        ),
    ]
