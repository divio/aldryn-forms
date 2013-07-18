# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin


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
    page = models.ForeignKey('cms.Page', verbose_name=_('CMS Page'), blank=True, null=True)
    url = models.URLField(_('Absolute URL'), blank=True, null=True)

    def __unicode__(self):
        return self.name


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=50, blank=True)

    def __unicode__(self):
        return self.legend or str(self.pk)


class FieldPlugin(CMSPlugin):
    """
    A general field model.

    The reason it's flat instead of having a nice structure is, as we read in
    CMSPlugin docs:

    > 1. subclasses of CMSPlugin *cannot be further subclassed*
    """

    label = models.CharField(_('Label'), max_length=50)
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

    def copy_relations(self, oldinstance):
        for option in oldinstance.option_set.all():
            option.pk = None  # copy on save
            option.field = self
            option.save()

    def __unicode__(self):
        return self.label


class Option(models.Model):

    value = models.CharField(_('Value'), max_length=50)
    field = models.ForeignKey(FieldPlugin, editable=False)

    def __unicode__(self):
        return self.value


class ButtonPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50)

    def __unicode__(self):
        return self.label
