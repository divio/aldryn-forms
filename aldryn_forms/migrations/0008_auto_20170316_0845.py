from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0007_auto_20170315_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True),
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True),
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='max_value',
            field=models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True),
        ),
    ]
