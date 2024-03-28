# Generated by Django 3.1.4 on 2021-11-17 10:31

import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('aldryn_forms', '0013_add_field_is_enable_autofill_from_url_params'),
    ]

    operations = [
        migrations.AddField(
            model_name='formplugin',
            name='condition_field',
            field=models.CharField(blank=True, help_text="This field is used to enable condition logic. If field matches the condition value then redirect and notification works as usual. If value of the field doesn't match the condition value field then custom redirect and notificaiton will be used.", max_length=512, null=True, verbose_name='Condition field'),
        ),
        migrations.AddField(
            model_name='formplugin',
            name='condition_value',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Condition field value'),
        ),
        migrations.AddField(
            model_name='formplugin',
            name='redirect_page_negative_condition',
            field=cms.models.fields.PageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_condition_false', to='cms.page', verbose_name='CMS Page (condition is false)'),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='action_backend',
            field=models.CharField(choices=[('none', 'None'), ('email_only', 'Email only'), ('default', 'Default')], default='default', max_length=15, verbose_name='Action backend'),
        ),
    ]
