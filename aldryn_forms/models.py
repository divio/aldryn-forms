# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.fields import PageField
from cms.models.pluginmodel import CMSPlugin

from emailit.api import send_mail

try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from .utils import get_form_render_data


class FormPlugin(CMSPlugin):

    REDIRECT_TO_PAGE = 'redirect_to_page'
    REDIRECT_TO_URL = 'redirect_to_url'
    REDIRECT_CHOICES = [
        (REDIRECT_TO_PAGE, _('CMS Page')),
        (REDIRECT_TO_URL, _('Absolute URL')),
    ]

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=50,
        help_text=_('Used to filter out form submissions.')
    )
    error_message = models.TextField(
        verbose_name=_('Error message'),
        blank=True,
        null=True,
        help_text=_('An error message that will be displayed if the form doesn\'t validate.'))
    redirect_type = models.CharField(
        verbose_name=_('Redirect to'),
        max_length=20,
        choices=REDIRECT_CHOICES,
        help_text=_('Where to redirect the user when the form has been successfully sent?')
    )
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)
    recipients = models.ManyToManyField(
        to=User,
        verbose_name=_('Recipients'),
        blank=True,
        limit_choices_to={'is_staff': True},
        help_text=_('People who will get the form content via e-mail.')
    )
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    def __unicode__(self):
        return self.name

    def copy_relations(self, oldinstance):
        for recipient in oldinstance.recipients.all():
            self.recipients.add(recipient)

    def get_notification_emails(self):
        return [x.email for x in self.recipients.all()]


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=50, blank=True)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    def __unicode__(self):
        return self.legend or str(self.pk)


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
    people_notified = models.ManyToManyField(
        to=User,
        verbose_name=_('admins notified'),
        blank=True,
        editable=False
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Form submission')
        verbose_name_plural = _('Form submissions')

    def __unicode__(self):
        return self.name

    def set_form_data(self, form):
        grouped_data = get_form_render_data(form)
        formatted_data = ['{0}: {1}'.format(*group) for group in grouped_data]
        self.data = '\n'.join(formatted_data)

    def send_notification_email(self, form, form_plugin):
        recipients = self.people_notified.values_list('email', flat=True)
        context = {
            'form_name': form_plugin.name,
            'form_data': get_form_render_data(form)
        }
        send_mail(
            recipients=recipients,
            context=context,
            template_base='aldryn_forms/emails/notification'
        )
