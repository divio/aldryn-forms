# Generated by Django 3.1.4 on 2021-11-17 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0014_auto_20211117_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formplugin',
            name='condition_field',
            field=models.CharField(blank=True, help_text="This field is used to enable condition logic. If field doesn't match the condition value then redirect and notification works as usual. If value of the field matches the condition value field then custom redirect and notification will be used.", max_length=512, null=True, verbose_name='Condition field'),
        ),
    ]
