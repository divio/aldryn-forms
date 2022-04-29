# Generated by Django 1.10.8 on 2017-12-20 19:33
from __future__ import unicode_literals

from django.db import migrations, models

import cms.models.fields

import djangocms_attributes_field.fields

from ..models import BaseFormPlugin


def forward_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FieldPlugin = apps.get_model('aldryn_forms', 'FieldPlugin')
    for field in FieldPlugin.objects.using(db_alias).iterator():
        for idx, option in enumerate(field.option_set.order_by('value'), start=1):
            option.position = idx * 10
            option.save()


def backward_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Option = apps.get_model('aldryn_forms', 'Option')
    Option.objects.using(db_alias).all().update(position=None)


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0009_auto_20171218_1049'),
        ('cms', '0006_auto_20140924_1110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={'verbose_name': 'Option', 'verbose_name_plural': 'Options'},
        ),
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='placeholder_text',
            field=models.CharField(blank=True,
                                   help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"',
                                   max_length=255, verbose_name='Placeholder text'),
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='placeholder_text',
            field=models.CharField(blank=True,
                                   help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"',
                                   max_length=255, verbose_name='Placeholder text'),
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='placeholder_text',
            field=models.CharField(blank=True,
                                   help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"',
                                   max_length=255, verbose_name='Placeholder text'),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='form_template',
            field=models.CharField(choices=BaseFormPlugin.FORM_TEMPLATES, default=BaseFormPlugin.DEFAULT_FORM_TEMPLATE,
                                   max_length=255, verbose_name='form template'),
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='placeholder_text',
            field=models.CharField(blank=True,
                                   help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"',
                                   max_length=255, verbose_name='Placeholder text'),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='placeholder_text',
            field=models.CharField(blank=True,
                                   help_text='Default text in a form. Disappears when user starts typing. Example: "email@example.com"',
                                   max_length=255, verbose_name='Placeholder text'),
        ),
        migrations.AlterModelOptions(
            name='option',
            options={'ordering': ('position',), 'verbose_name': 'Option', 'verbose_name_plural': 'Options'},
        ),
        migrations.RenameField(
            model_name='formplugin',
            old_name='page',
            new_name='redirect_page',
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='redirect_page',
            field=cms.models.fields.PageField(blank=True, null=True, on_delete=models.deletion.SET_NULL,
                                              to='cms.Page', verbose_name='CMS Page'),
        ),
        migrations.AddField(
            model_name='emailfieldplugin',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='emailfieldplugin',
            name='initial_value',
            field=models.CharField(blank=True, help_text='Default value of field.', max_length=255, verbose_name='Initial value'),
        ),
        migrations.AddField(
            model_name='emailfieldplugin',
            name='name',
            field=models.CharField(blank=True, help_text='Used to set the field name', max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='fieldplugin',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='fieldplugin',
            name='initial_value',
            field=models.CharField(blank=True, help_text='Default value of field.', max_length=255, verbose_name='Initial value'),
        ),
        migrations.AddField(
            model_name='fieldplugin',
            name='name',
            field=models.CharField(blank=True, help_text='Used to set the field name', max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='fileuploadfieldplugin',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='fileuploadfieldplugin',
            name='initial_value',
            field=models.CharField(blank=True, help_text='Default value of field.', max_length=255, verbose_name='Initial value'),
        ),
        migrations.AddField(
            model_name='fileuploadfieldplugin',
            name='name',
            field=models.CharField(blank=True, help_text='Used to set the field name', max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='formplugin',
            name='form_attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='imageuploadfieldplugin',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='imageuploadfieldplugin',
            name='initial_value',
            field=models.CharField(blank=True, help_text='Default value of field.', max_length=255, verbose_name='Initial value'),
        ),
        migrations.AddField(
            model_name='imageuploadfieldplugin',
            name='name',
            field=models.CharField(blank=True, help_text='Used to set the field name', max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='textareafieldplugin',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(blank=True, default=dict, verbose_name='Attributes'),
        ),
        migrations.AddField(
            model_name='textareafieldplugin',
            name='initial_value',
            field=models.CharField(blank=True, help_text='Default value of field.', max_length=255, verbose_name='Initial value'),
        ),
        migrations.AddField(
            model_name='textareafieldplugin',
            name='name',
            field=models.CharField(blank=True, help_text='Used to set the field name', max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='redirect_type',
            field=models.CharField(blank=True, choices=[('redirect_to_page', 'CMS Page'), ('redirect_to_url', 'Absolute URL')], help_text='Where to redirect the user when the form has been successfully sent?', max_length=20, verbose_name='Redirect to'),
        ),

        # 1: create field as nullable
        migrations.AddField(
            model_name='option',
            name='position',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Position'),
        ),

        # 2: populate field
        migrations.RunPython(forward_migration, backward_migration),

        # 3: update field to non-nullable
        migrations.AlterField(
            model_name='option',
            name='position',
            field=models.PositiveIntegerField(blank=True, verbose_name='Position'),
        ),
    ]
