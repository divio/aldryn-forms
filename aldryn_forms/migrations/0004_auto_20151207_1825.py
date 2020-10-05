from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0003_auto_20151207_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='form name', max_length=50, editable=False, db_index=True)),
                ('data', models.TextField(editable=False, blank=True)),
                ('recipients', models.TextField(help_text='People who got a notification when form was submitted.', verbose_name='users notified', editable=False, blank=True)),
                ('language', models.CharField(default=settings.LANGUAGE_CODE, max_length=10, verbose_name='form language', choices=settings.LANGUAGES)),
                ('form_url', models.CharField(max_length=255, verbose_name='form url', blank=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Form submission',
                'verbose_name_plural': 'Form submissions',
            },
        ),
        migrations.AlterModelOptions(
            name='formdata',
            options={'verbose_name': 'Form submission (Old)', 'verbose_name_plural': 'Form submissions (Old)'},
        ),
    ]
