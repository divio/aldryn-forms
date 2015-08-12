# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.folder
from django.conf import settings
import cms.models.fields
import sizefield.models


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Field is required')),
                ('required_message', models.TextField(help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, verbose_name='Error message', blank=True)),
                ('placeholder_text', models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=50, verbose_name='Placeholder text', blank=True)),
                ('help_text', models.TextField(help_text='Explanatory text displayed next to input field. Just like this one.', null=True, verbose_name='Help text', blank=True)),
                ('min_value', models.PositiveIntegerField(null=True, verbose_name='Min value', blank=True)),
                ('max_value', models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
                ('email_send_notification', models.BooleanField(default=False, help_text='When checked, the value of this field will be used to send an email notification.', verbose_name=b'send notification when form is submitted')),
                ('email_subject', models.CharField(default=b'', help_text='Used as the email subject when email_send_notification is checked.', max_length=200, verbose_name='email subject', blank=True)),
                ('email_body', models.TextField(default=b'', help_text='Additional body text used when email notifications are active.', verbose_name='Additional email body', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Field is required')),
                ('required_message', models.TextField(help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, verbose_name='Error message', blank=True)),
                ('placeholder_text', models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=50, verbose_name='Placeholder text', blank=True)),
                ('help_text', models.TextField(help_text='Explanatory text displayed next to input field. Just like this one.', null=True, verbose_name='Help text', blank=True)),
                ('min_value', models.PositiveIntegerField(null=True, verbose_name='Min value', blank=True)),
                ('max_value', models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FieldsetPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('legend', models.CharField(max_length=50, verbose_name='Legend', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FileUploadFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Field is required')),
                ('required_message', models.TextField(help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, verbose_name='Error message', blank=True)),
                ('placeholder_text', models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=50, verbose_name='Placeholder text', blank=True)),
                ('help_text', models.TextField(help_text='Explanatory text displayed next to input field. Just like this one.', null=True, verbose_name='Help text', blank=True)),
                ('min_value', models.PositiveIntegerField(null=True, verbose_name='Min value', blank=True)),
                ('max_value', models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
                ('max_size', sizefield.models.FileSizeField(help_text='The maximum file size of the upload, in bytes. You can use common size suffixes (kB, MB, GB, ...).', null=True, verbose_name='Maximum file size', blank=True)),
                ('upload_to', filer.fields.folder.FilerFolderField(verbose_name='Upload files to', to='filer.Folder', help_text='Select a folder to which all files submitted through this field will be uploaded to.')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FormButtonPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label')),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='FormData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, editable=False, db_index=True)),
                ('data', models.TextField(null=True, editable=False, blank=True)),
                ('language', models.CharField(default=b'en', max_length=10, verbose_name='language', choices=[(b'de', b'German'), (b'en', b'English'), (b'fr', b'French')])),
                ('people_notified', models.TextField(help_text='People who got a notification when form was submitted.', verbose_name='users notified', editable=False, blank=True)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Form submission',
                'verbose_name_plural': 'Form submissions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('name', models.CharField(help_text='Used to filter out form submissions.', max_length=50, verbose_name='Name')),
                ('error_message', models.TextField(help_text="An error message that will be displayed if the form doesn't validate.", null=True, verbose_name='Error message', blank=True)),
                ('success_message', models.TextField(help_text='An success message that will be displayed.', null=True, verbose_name='Success message', blank=True)),
                ('redirect_type', models.CharField(help_text='Where to redirect the user when the form has been successfully sent?', max_length=20, verbose_name='Redirect to', choices=[(b'redirect_to_page', 'CMS Page'), (b'redirect_to_url', 'Absolute URL')])),
                ('url', models.URLField(null=True, verbose_name='Absolute URL', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
                ('form_template', models.CharField(default=b'aldryn_forms/form.html', max_length=200, verbose_name='form template', choices=[(b'aldryn_forms/form.html', 'Default')])),
                ('page', cms.models.fields.PageField(verbose_name='CMS Page', blank=True, to='cms.Page', null=True)),
                ('recipients', models.ManyToManyField(help_text='People who will get the form content via e-mail.', to=settings.AUTH_USER_MODEL, verbose_name='Recipients', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ImageUploadFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Field is required')),
                ('required_message', models.TextField(help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, verbose_name='Error message', blank=True)),
                ('placeholder_text', models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=50, verbose_name='Placeholder text', blank=True)),
                ('help_text', models.TextField(help_text='Explanatory text displayed next to input field. Just like this one.', null=True, verbose_name='Help text', blank=True)),
                ('min_value', models.PositiveIntegerField(null=True, verbose_name='Min value', blank=True)),
                ('max_value', models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
                ('max_size', sizefield.models.FileSizeField(help_text='The maximum file size of the upload, in bytes. You can use common size suffixes (kB, MB, GB, ...).', null=True, verbose_name='Maximum file size', blank=True)),
                ('max_width', models.PositiveIntegerField(help_text='The maximum width of the uploaded image, in pixels.', null=True, verbose_name='Maximum image width', blank=True)),
                ('max_height', models.PositiveIntegerField(help_text='The maximum height of the uploaded image, in pixels.', null=True, verbose_name='Maximum image height', blank=True)),
                ('upload_to', filer.fields.folder.FilerFolderField(verbose_name='Upload files to', to='filer.Folder', help_text='Select a folder to which all files submitted through this field will be uploaded to.')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=50, verbose_name='Value')),
                ('default_value', models.BooleanField(default=False, verbose_name='Default')),
                ('field', models.ForeignKey(editable=False, to='aldryn_forms.FieldPlugin')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextAreaFieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('label', models.CharField(max_length=50, verbose_name='Label', blank=True)),
                ('required', models.BooleanField(default=True, verbose_name='Field is required')),
                ('required_message', models.TextField(help_text='Error message displayed if the required field is left empty. Default: "This field is required".', null=True, verbose_name='Error message', blank=True)),
                ('placeholder_text', models.CharField(help_text='Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"', max_length=50, verbose_name='Placeholder text', blank=True)),
                ('help_text', models.TextField(help_text='Explanatory text displayed next to input field. Just like this one.', null=True, verbose_name='Help text', blank=True)),
                ('min_value', models.PositiveIntegerField(null=True, verbose_name='Min value', blank=True)),
                ('max_value', models.PositiveIntegerField(null=True, verbose_name='Max value', blank=True)),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom css classes', blank=True)),
                ('text_area_columns', models.PositiveIntegerField(null=True, verbose_name='columns', blank=True)),
                ('text_area_rows', models.PositiveIntegerField(null=True, verbose_name='rows', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
