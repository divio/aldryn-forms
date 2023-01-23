from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0006_auto_20160821_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='email_subject',
            field=models.CharField(default='', help_text='Used as the email subject when email_send_notification is checked.', max_length=255, verbose_name='email subject', blank=True),
        ),
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label', blank=True),
        ),
        migrations.AlterField(
            model_name='emailfieldplugin',
            name='placeholder_text',
            field=models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=255, verbose_name='Placeholder text', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldplugin',
            name='placeholder_text',
            field=models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=255, verbose_name='Placeholder text', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldsetplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='fieldsetplugin',
            name='legend',
            field=models.CharField(max_length=255, verbose_name='Legend', blank=True),
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label', blank=True),
        ),
        migrations.AlterField(
            model_name='fileuploadfieldplugin',
            name='placeholder_text',
            field=models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=255, verbose_name='Placeholder text', blank=True),
        ),
        migrations.AlterField(
            model_name='formbuttonplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='formbuttonplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label'),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='form_template',
            field=models.CharField(default='aldryn_forms/form.html', max_length=255, verbose_name='form template', choices=[('aldryn_forms/form.html', 'Default'), ('aldryn_forms/horizontal/form.html', 'Horizontal')]),
        ),
        migrations.AlterField(
            model_name='formplugin',
            name='name',
            field=models.CharField(help_text='Used to filter out form submissions.', max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='formsubmission',
            name='name',
            field=models.CharField(verbose_name='form name', max_length=255, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label', blank=True),
        ),
        migrations.AlterField(
            model_name='imageuploadfieldplugin',
            name='placeholder_text',
            field=models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=255, verbose_name='Placeholder text', blank=True),
        ),
        migrations.AlterField(
            model_name='option',
            name='value',
            field=models.CharField(max_length=255, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='custom_classes',
            field=models.CharField(max_length=255, verbose_name='custom css classes', blank=True),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='label',
            field=models.CharField(max_length=255, verbose_name='Label', blank=True),
        ),
        migrations.AlterField(
            model_name='textareafieldplugin',
            name='placeholder_text',
            field=models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=255, verbose_name='Placeholder text', blank=True),
        ),
    ]
