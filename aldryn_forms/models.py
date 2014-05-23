# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.fields import PageField
from cms.models.pluginmodel import CMSPlugin

try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class FormPlugin(CMSPlugin):

    REDIRECT_TO_PAGE = 'redirect_to_page'
    REDIRECT_TO_URL = 'redirect_to_url'
    REDIRECT_CHOICES = [
        (REDIRECT_TO_PAGE, _('CMS Page')),
        (REDIRECT_TO_URL, _('Absolute URL')),
    ]

    name = models.CharField(_('Name'), max_length=50, help_text=_('Used to filter out form submissions.'))
    error_message = models.TextField(_('Error message'), blank=True, null=True,
                                     help_text=_('An error message that will be displayed if the form doesn\'t '
                                                 'validate.'))
    redirect_type = models.CharField(_('Redirect to'), max_length=20, choices=REDIRECT_CHOICES,
                                     help_text=_('Where to redirect the user when the form has been '
                                                 'successfully sent?'))
    page = PageField(verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)
    recipients = models.ManyToManyField(User, verbose_name=_('Recipients'), blank=True,
                                        # through='aldryn_forms.FormToRecipient',
                                        help_text=_('People who will get the form content via e-mail.'))
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
    required_message = models.TextField(_('Error message'), blank=True, null=True,
                                        help_text=_('Error message displayed if the required field is left '
                                                    'empty. Default: "This field is required".'))
    placeholder_text = models.CharField(_('Placeholder text'), max_length=50, blank=True,
                                        help_text=_('Default text in a form. Disapears when user starts typing. '
                                                    'Example: "email@exmaple.com"'))
    help_text = models.TextField(_('Help text'), blank=True, null=True,
                                 help_text=_('Explanatory text displayed next to input field. Just like this one.'))

    # for text field those are min and max length
    # for multiple select those are min and max number of choices
    min_value = models.PositiveIntegerField(_('Min value'), blank=True, null=True)
    max_value = models.PositiveIntegerField(_('Max value'), blank=True, null=True)

    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.label or str(self.pk)


class FieldPlugin(FieldPluginBase):

    class Meta:
        db_table = 'cmsplugin_fieldplugin'

    def copy_relations(self, oldinstance):
        for option in oldinstance.option_set.all():
            option.pk = None  # copy on save
            option.field = self
            option.save()


class TextAreaFieldPlugin(FieldPluginBase):

    text_area_columns = models.PositiveIntegerField(verbose_name=_('columns'), blank=True, null=True)
    text_area_rows = models.PositiveIntegerField(verbose_name=_('rows'), blank=True, null=True)


class Option(models.Model):

    field = models.ForeignKey(FieldPlugin, editable=False)
    value = models.CharField(_('Value'), max_length=50)
    default_value = models.BooleanField(_('Default'), default=False)

    def __unicode__(self):
        return self.value


class ButtonPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50)
    custom_classes = models.CharField(verbose_name=_('custom css classes'), max_length=200, blank=True)

    def __unicode__(self):
        return self.label


class FormData(models.Model):

    name = models.CharField(max_length=50, db_index=True, editable=False)
    data = models.TextField(blank=True, null=True, editable=False)
    people_notified = models.ManyToManyField(User, blank=True, editable=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Form submission')
        verbose_name_plural = _('Form submissions')

    def __unicode__(self):
        return self.name
