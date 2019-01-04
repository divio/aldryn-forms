# Generated by Django 2.0 on 2019-01-04 11:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0011_auto_20180110_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formplugin',
            name='recipients',
            field=models.ManyToManyField(blank=True, help_text='People who will get the form content via e-mail.', limit_choices_to={'is_staff': True}, to=settings.AUTH_USER_MODEL, verbose_name='Recipients'),
        ),
    ]
