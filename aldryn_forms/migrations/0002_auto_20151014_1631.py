from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


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
            field=models.CharField(default='en', max_length=10, verbose_name='language', choices=[('en', 'en'), ('fr', 'fr'), ('de', 'de')]),
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
