# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aldryn_forms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('theme', models.CharField(help_text='Provides the base theme for the email.', max_length=200, verbose_name='theme', choices=[(b'default', 'default')])),
                ('to_name', models.CharField(max_length=200, verbose_name='to name', blank=True)),
                ('to_email', models.CharField(max_length=200, verbose_name='to email', blank=True)),
                ('from_name', models.CharField(max_length=200, verbose_name='from name', blank=True)),
                ('from_email', models.CharField(max_length=200, verbose_name='from email', blank=True)),
                ('subject', models.CharField(max_length=200, verbose_name='subject', blank=True)),
                ('body_text', models.TextField(help_text='used when rendering the email in text only mode.', verbose_name='email body (txt)', blank=True)),
                ('body_html', djangocms_text_ckeditor.fields.HTMLField(help_text='used when rendering the email in html.', verbose_name='email body (html)', blank=True)),
                ('to_user', models.ForeignKey(verbose_name='to user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailNotificationFormPlugin',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('aldryn_forms.formplugin',),
        ),
        migrations.AddField(
            model_name='emailnotification',
            name='form',
            field=models.ForeignKey(related_name='email_notifications', to='email_notifications.EmailNotificationFormPlugin'),
            preserve_default=True,
        ),
    ]
