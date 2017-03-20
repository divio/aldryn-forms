# -*- coding: utf-8 -*-
from functools import partial
import json
from collections import defaultdict, namedtuple

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.datastructures import SortedDict
except ImportError:
    from collections import OrderedDict as SortedDict

from cms.models.fields import PageField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.plugins import build_plugin_tree, downcast_plugins

from filer.fields.folder import FilerFolderField

from sizefield.models import FileSizeField

from . import compat
from .helpers import is_form_element


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


if compat.LTE_DJANGO_1_6:
    # related_name='%(app_label)s_%(class)s' does not work on  Django 1.6
    CMSPluginField = partial(
        models.OneToOneField,
        to=CMSPlugin,
        related_name='+',
        parent_link=True,
    )
else:
    # Once djangoCMS < 3.3.1 support is dropped
    # Remove the explicit cmsplugin_ptr field declarations
    CMSPluginField = partial(
        models.OneToOneField,
        to=CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
    )

FieldData = namedtuple(
    'FieldData',
    field_names=['label', 'value']
)
FormField = namedtuple(
    'FormField',
    field_names=[
        'name',
        'label',
        'plugin_instance',
        'field_occurrence',
        'field_type_occurrence',
    ]
)
Recipient = namedtuple(
    'Recipient',
    field_names=['name', 'email']
)
BaseSerializedFormField = namedtuple(
    'SerializedFormField',
    field_names=[
        'name',
        'label',
        'field_occurrence',
        'value',
    ]
)


class SerializedFormField(BaseSerializedFormField):

    # For _asdict() with Py3K
    __slots__ = ()

    @property
    def field_id(self):
        field_label = self.label.strip()

        if field_label:
            field_as_string = u'{}-{}'.format(field_label, self.field_type)
        else:
            field_as_string = self.name
        field_id = u'{}:{}'.format(field_as_string, self.field_occurrence)
        return field_id

    @property
    def field_type_occurrence(self):
        return self.name.rpartition('_')[1]

    @property
    def field_type(self):
        return self.name.rpartition('_')[0]


@python_2_unicode_compatible
class FormPlugin(CMSPlugin):

    FALLBACK_FORM_TEMPLATE = 'aldryn_forms/form.html'
    DEFAULT_FORM_TEMPLATE = getattr(
        settings, 'ALDRYN_FORMS_DEFAULT_TEMPLATE', FALLBACK_FORM_TEMPLATE)

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
        max_length=255,
        help_text=_('Used to filter out form submissions.')
    )
    error_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('An error message that will be displayed if the form '
                    'doesn\'t validate.')
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
        help_text=_('Where to redirect the user when the form has been '
                    'successfully sent?')
    )
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    form_template = models.CharField(
        verbose_name=_('form template'),
        max_length=255,
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

    cmsplugin_ptr = CMSPluginField()

    def __str__(self):
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

        # A field occurrence is how many times does a field
        # with the same label and type appear within the same form.
        # This is used as an identifier for the field within multiple forms.
        field_occurrences = defaultdict(lambda: 1)

        # A field type occurrence is how many times does a field
        # with the same type appear within the same form.
        # This is used as an identifier for the field within this form.
        field_type_occurrences = defaultdict(lambda: 1)

        form_elements = self.get_form_elements()
        is_form_field = lambda plugin: issubclass(
            plugin.get_plugin_class(), Field)
        field_plugins = [
            plugin for plugin in form_elements if is_form_field(plugin)]

        for field_plugin in field_plugins:
            field_type = field_plugin.field_type

            if field_type in field_type_occurrences:
                field_type_occurrences[field_type] += 1

            field_type_occurrence = field_type_occurrences[field_type]

            field_name = u'{0}_{1}'.format(field_type, field_type_occurrence)
            field_label = field_plugin.get_label()

            if field_label:
                field_id = u'{0}_{1}'.format(field_type, field_label)
            else:
                field_id = field_name

            if field_id in field_occurrences:
                field_occurrences[field_id] += 1

            field = FormField(
                name=field_name,
                label=field_label,
                plugin_instance=field_plugin,
                field_occurrence=field_occurrences[field_id],
                field_type_occurrence=field_type_occurrence,
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
            descendants = self.get_descendants().order_by('path')
            # Set parent_id to None in order to
            # fool the build_plugin_tree function.
            # This is sadly necessary to avoid getting all nodes
            # higher than the form.
            parent_id = self.parent_id
            self.parent_id = None
            # Important that this is a list in order to modify
            # the current instance
            descendants_with_self = [self] + list(descendants)
            # Let the cms build the tree
            build_plugin_tree(descendants_with_self)
            # Set back the original parent
            self.parent_id = parent_id

        if self._form_elements is None:
            children = get_nested_plugins(self)
            children_instances = downcast_plugins(children)
            self._form_elements = [
                p for p in children_instances if is_form_element(p)]
        return self._form_elements


@python_2_unicode_compatible
class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=255, blank=True)
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    cmsplugin_ptr = CMSPluginField()

    def __str__(self):
        return self.legend or text_type(self.pk)


@python_2_unicode_compatible
class FieldPluginBase(CMSPlugin):

    label = models.CharField(_('Label'), max_length=255, blank=True)
    required = models.BooleanField(_('Field is required'), default=False)
    required_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('Error message displayed if the required field is left '
                    'empty. Default: "This field is required".')
    )
    placeholder_text = models.CharField(
        verbose_name=_('Placeholder text'),
        max_length=255,
        blank=True,
        help_text=_('Default text in a form. Disappears when user starts '
                    'typing. Example: "email@exmaple.com"')
    )
    help_text = models.TextField(
        verbose_name=_('Help text'),
        blank=True,
        null=True,
        help_text=_('Explanatory text displayed next to input field. Just like '
                    'this one.')
    )

    # for text field those are min and max length
    # for multiple select those are min and max number of choices
    min_value = models.PositiveIntegerField(
        _('Min value'),
        blank=True,
        null=True,
    )

    max_value = models.PositiveIntegerField(
        _('Max value'),
        blank=True,
        null=True,
    )

    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    cmsplugin_ptr = CMSPluginField()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(FieldPluginBase, self).__init__(*args, **kwargs)
        if self.plugin_type:
            attribute = 'is_%s' % self.field_type
            setattr(self, attribute, True)

    def __str__(self):
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

    text_area_columns = models.PositiveIntegerField(
        verbose_name=_('columns'), blank=True, null=True)
    text_area_rows = models.PositiveIntegerField(
        verbose_name=_('rows'), blank=True, null=True)


class EmailFieldPlugin(FieldPluginBase):
    email_send_notification = models.BooleanField(
        verbose_name=('send notification when form is submitted'),
        default=False,
        help_text=_('When checked, the value of this field will be used to '
                    'send an email notification.')
    )
    email_subject = models.CharField(
        verbose_name=_('email subject'),
        max_length=255,
        blank=True,
        default='',
        help_text=_('Used as the email subject when email_send_notification '
                    'is checked.')
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


@python_2_unicode_compatible
class Option(models.Model):

    field = models.ForeignKey(FieldPlugin, editable=False)
    value = models.CharField(_('Value'), max_length=255)
    default_value = models.BooleanField(_('Default'), default=False)

    def __str__(self):
        return self.value


@python_2_unicode_compatible
class FormButtonPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=255)
    custom_classes = models.CharField(
        verbose_name=_('custom css classes'), max_length=255, blank=True)
    cmsplugin_ptr = CMSPluginField()

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class FormSubmission(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_('form name'),
        db_index=True,
        editable=False
    )
    data = models.TextField(blank=True, editable=False)
    recipients = models.TextField(
        verbose_name=_('users notified'),
        blank=True,
        help_text=_('People who got a notification when form was submitted.'),
        editable=False,
    )
    language = models.CharField(
        verbose_name=_('form language'),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )
    form_url = models.CharField(
        verbose_name=_('form url'),
        max_length=255,
        blank=True,
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _('Form submission')
        verbose_name_plural = _('Form submissions')

    def __str__(self):
        return self.name

    def _form_data_hook(self, data, occurrences):
        field_label = data['label'].strip()

        if field_label:
            field_type = data['name'].rpartition('_')[0]
            field_id = u'{}_{}'.format(field_type, field_label)
        else:
            field_id = data['name']

        if field_id in occurrences:
            occurrences[field_id] += 1

        data['field_occurrence'] = occurrences[field_id]
        return SerializedFormField(**data)

    def _recipients_hook(self, data):
        return Recipient(**data)

    def get_form_data(self):
        occurrences = defaultdict(lambda: 1)

        data_hook = partial(self._form_data_hook, occurrences=occurrences)

        try:
            form_data = json.loads(
                self.data,
                object_hook=data_hook,
            )
        except ValueError:
            # TODO: Log this?
            form_data = []
        return form_data

    def get_recipients(self):
        try:
            recipients = json.loads(
                self.recipients,
                object_hook=self._recipients_hook
            )
        except ValueError:
            # TODO: Log this?
            recipients = []
        return recipients

    def set_form_data(self, form):
        fields = form.get_serialized_fields(is_confirmation=False)
        fields_as_dicts = [field._asdict() for field in fields]

        self.data = json.dumps(fields_as_dicts)

    def set_recipients(self, recipients):
        raw_recipients = [
            {'name': rec[0], 'email': rec[1]} for rec in recipients]
        self.recipients = json.dumps(raw_recipients)
