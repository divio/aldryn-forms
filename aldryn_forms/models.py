# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
from distutils.version import LooseVersion

from django.conf import settings
from django.db import models
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

import cms
from cms.models.fields import PageField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.plugins import downcast_plugins

from filer.fields.folder import FilerFolderField

from sizefield.models import FileSizeField

from .helpers import is_form_element


CMS_31 = LooseVersion(cms.__version__) >= LooseVersion('3.1')
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

FieldData = namedtuple(
    'FieldData',
    field_names=['label', 'value']
)
FormField = namedtuple(
    'FormField',
    field_names=['name', 'label', 'plugin_instance', 'occurrence']
)
SerializedFormField = namedtuple(
    'SerializedFormField',
    field_names=['name', 'label', 'value']
)


class FormPlugin(CMSPlugin):

    FALLBACK_FORM_TEMPLATE = 'aldryn_forms/form.html'
    DEFAULT_FORM_TEMPLATE = getattr(settings, 'ALDRYN_FORMS_DEFAULT_TEMPLATE', FALLBACK_FORM_TEMPLATE)

    FORM_TEMPLATES = ((DEFAULT_FORM_TEMPLATE, _('Default')),)

    if hasattr(settings, 'ALDRYN_FORMS_TEMPLATES'):
        FORM_TEMPLATES += settings.ALDRYN_FORMS_TEMPLATES

    REDIRECT_TO_PAGE = 'redirect_to_page'
    REDIRECT_TO_URL = 'redirect_to_url'
    REDIRECT_CHOICES = [
        (REDIRECT_TO_PAGE, _('CMS Page')),
        (REDIRECT_TO_URL, _('Absolute URL')),
    ]

    _form_elements = None
    _form_field_key_cache = None

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=50,
        help_text=_('Used to filter out form submissions.')
    )
    error_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('An error message that will be displayed if the form doesn\'t validate.')
    )
    success_message = models.TextField(
        verbose_name=_('Success message'),
        blank=True,
        null=True,
        help_text=_('An success message that will be displayed.')
    )
    redirect_type = models.CharField(
        verbose_name=_('Redirect to'),
        max_length=20,
        choices=REDIRECT_CHOICES,
        help_text=_('Where to redirect the user when the form has been successfully sent?')
    )
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)
    form_template = models.CharField(
        verbose_name=_('form template'),
        max_length=200,
        choices=FORM_TEMPLATES,
        default=DEFAULT_FORM_TEMPLATE,
    )

    # Staff notification email settings
    recipients = models.ManyToManyField(
        to=AUTH_USER_MODEL,
        verbose_name=_('Recipients'),
        blank=True,
        limit_choices_to={'is_staff': True},
        help_text=_('People who will get the form content via e-mail.')
    )

    def __unicode__(self):
        return self.name

    def copy_relations(self, oldinstance):
        for recipient in oldinstance.recipients.all():
            self.recipients.add(recipient)

    def get_submit_button(self):
        from .cms_plugins import SubmitButton

        form_elements = self.get_form_elements()

        for element in form_elements:
            plugin_class = element.get_plugin_class()

            if issubclass(plugin_class, SubmitButton):
                return element
        return

    def get_form_fields(self):
        from .cms_plugins import Field

        fields = []
        occurrences = defaultdict(int)

        form_elements = self.get_form_elements()
        is_form_field = lambda plugin: issubclass(plugin.get_plugin_class(), Field)
        field_plugins = [plugin for plugin in form_elements if is_form_field(plugin)]

        for field_plugin in field_plugins:
            field_type = field_plugin.field_type
            occurrences[field_type] += 1
            occurrence = occurrences[field_type]

            field_name = u'{0}_{1}'.format(field_type, occurrence)
            field_label = field_plugin.get_label() or field_name

            field = FormField(
                name=field_name,
                label=field_label,
                plugin_instance=field_plugin,
                occurrence=occurrence,
            )
            fields.append(field)
        return fields

    def get_form_field_name(self, field):
        if self._form_field_key_cache is None:
            self._form_field_key_cache = {}

        if not field.pk in self._form_field_key_cache:
            fields_by_key = self.get_form_fields_by_name()

            for name, _field in fields_by_key.items():
                self._form_field_key_cache[_field.plugin_instance.pk] = name
        return self._form_field_key_cache[field.pk]

    def get_form_fields_as_choices(self):
        fields = self.get_form_fields()

        for field in fields:
            yield (field.name, field.label)

    def get_form_fields_by_name(self):
        fields = self.get_form_fields()
        fields_by_name = SortedDict((field.name, field) for field in fields)
        return fields_by_name

    def get_form_elements(self):
        from .utils import get_nested_plugins

        if self.child_plugin_instances is None:
            # 3.1 and 3.0 compatibility
            if CMS_31:
                # default ordering is by path
                ordering = ('path', 'position')
            else:
                ordering = ('tree_id', 'level', 'position')
            self.child_plugin_instances = self.get_descendants().order_by(*ordering)

        if self._form_elements is None:
            children = get_nested_plugins(self)
            children_instances = downcast_plugins(children)
            self._form_elements = [plugin for plugin in children_instances if is_form_element(plugin)]
        return self._form_elements


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=50, blank=True)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    def __unicode__(self):
        return self.legend or unicode(self.pk)


class FieldPluginBase(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50, blank=True)
    required = models.BooleanField(_('Field is required'), default=True)
    required_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('Error message displayed if the required field is left empty. Default: "This field is required".')
    )
    placeholder_text = models.CharField(
        verbose_name=_('Placeholder text'),
        max_length=50,
        blank=True,
        help_text=_('Default text in a form. Disappears when user starts typing. Example: "email@exmaple.com"')
    )
    help_text = models.TextField(
        verbose_name=_('Help text'),
        blank=True,
        null=True,
        help_text=_('Explanatory text displayed next to input field. Just like this one.')
    )

    # for text field those are min and max length
    # for multiple select those are min and max number of choices
    min_value = models.PositiveIntegerField(_('Min value'), blank=True, null=True)
    max_value = models.PositiveIntegerField(_('Max value'), blank=True, null=True)

    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(FieldPluginBase, self).__init__(*args, **kwargs)
        if self.plugin_type:
            attribute = 'is_%s' % self.field_type
            setattr(self, attribute, True)

    def __unicode__(self):
        return self.label or str(self.pk)

    @property
    def field_type(self):
        return self.plugin_type.lower()

    def get_label(self):
        return self.label or self.placeholder_text


class FieldPlugin(FieldPluginBase):

    def copy_relations(self, oldinstance):
        for option in oldinstance.option_set.all():
            option.pk = None  # copy on save
            option.field = self
            option.save()


class TextAreaFieldPlugin(FieldPluginBase):

    text_area_columns = models.PositiveIntegerField(verbose_name=_('columns'), blank=True, null=True)
    text_area_rows = models.PositiveIntegerField(verbose_name=_('rows'), blank=True, null=True)


class EmailFieldPlugin(FieldPluginBase):
    email_send_notification = models.BooleanField(
        verbose_name=('send notification when form is submitted'),
        default=False,
        help_text=_('When checked, the value of this field will be used to send an email notification.')
    )
    email_subject = models.CharField(
        verbose_name=_('email subject'),
        max_length=200,
        blank=True,
        default='',
        help_text=_('Used as the email subject when email_send_notification is checked.')
    )
    email_body = models.TextField(
        verbose_name=_('Additional email body'),
        blank=True,
        default='',
        help_text=_('Additional body text used when email notifications '
                    'are active.')
    )


class FileFieldPluginBase(FieldPluginBase):
    upload_to = FilerFolderField(
        verbose_name=_('Upload files to'),
        help_text=_('Select a folder to which all files submitted through '
                    'this field will be uploaded to.')
    )
    max_size = FileSizeField(
        verbose_name=_('Maximum file size'),
        null=True, blank=True,
        help_text=_('The maximum file size of the upload, in bytes. You can '
                    'use common size suffixes (kB, MB, GB, ...).')
    )

    class Meta:
        abstract = True


class FileUploadFieldPlugin(FileFieldPluginBase):
    pass


class ImageUploadFieldPlugin(FileFieldPluginBase):
    max_width = models.PositiveIntegerField(
        verbose_name=_('Maximum image width'),
        null=True, blank=True,
        help_text=_('The maximum width of the uploaded image, in pixels.')
    )
    max_height = models.PositiveIntegerField(
        verbose_name=_('Maximum image height'),
        null=True, blank=True,
        help_text=_('The maximum height of the uploaded image, in pixels.')
    )


class Option(models.Model):

    field = models.ForeignKey(FieldPlugin, editable=False)
    value = models.CharField(_('Value'), max_length=50)
    default_value = models.BooleanField(_('Default'), default=False)

    def __unicode__(self):
        return self.value


class FormButtonPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    def __unicode__(self):
        return self.label


class FormData(models.Model):

    name = models.CharField(max_length=50, db_index=True, editable=False)
    data = models.TextField(blank=True, null=True, editable=False)
    language = models.CharField(
        verbose_name=_('language'),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )
    people_notified = models.TextField(
        verbose_name=_('users notified'),
        blank=True,
        help_text=_('People who got a notification when form was submitted.'),
        editable=False,
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Form submission')
        verbose_name_plural = _('Form submissions')

    def __unicode__(self):
        return self.name

    def get_data(self):
        fields = self.data.splitlines()
        # this will be a list of dictionaries mapping field name to value.
        # we use this approach because using field name as key might result in overriding values
        # since fields can have the same name
        form_data = []

        for field in fields:
            bits = field.split(':')
            # this is an unfortunate design flaw on this model.
            # ":" was chosen as delimiter to separate field_name from field value
            # and so if a user ever enters ":" in any one of the two then we can't
            # really reliable get the name or value, so for now ignore that field :(
            if len(bits) == 2:
                data = FieldData(label=bits[0], value=bits[1])
                form_data.append(data)
        return form_data

    def set_form_data(self, form):
        grouped_data = form.get_serialized_field_choices()
        formatted_data = [u'{0}: {1}'.format(*group) for group in grouped_data]
        self.data = u'\n'.join(formatted_data)

    def set_users_notified(self, recipients):
        self.people_notified = ':::'.join(recipients)
