from __future__ import unicode_literals

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


APP_LABEL = 'email_notifications'
MODEL_NAME = 'emailnotificationformplugin'
VERBOSE_MODEL_NAME = 'form (advanced)'
ACTIONS = ('add', 'change', 'delete')


def get_content_type():
    try:
        return ContentType.objects.get(app_label=APP_LABEL, model=MODEL_NAME)
    except ContentType.DoesNotExist:
        return None


def forwards(apps, schema_editor):
    content_type = get_content_type()
    if content_type:
        for action in ACTIONS:
            Permission.objects.get_or_create(
                codename='{}_{}'.format(action, MODEL_NAME),
                content_type=content_type,
                defaults={
                    'name': 'Can {} {}'.format(action, VERBOSE_MODEL_NAME)
                }
            )


def backwards(apps, schema_editor):
    content_type = get_content_type()
    if content_type:
        codenames = [
            '{}_{}'.format(action, MODEL_NAME)
            for action in ACTIONS
        ]

        Permission.objects.filter(
            codename__in=codenames,
            content_type=content_type,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('email_notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            forwards,
            reverse_code=backwards,
        )
    ]
