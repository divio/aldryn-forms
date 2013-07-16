# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin


class FormPlugin(CMSPlugin):

    name = models.CharField(_('Name'), max_length=50, help_text=_('Used to filter out form submissions.'))

    def __unicode__(self):
        return self.name


class FieldPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50)
    required = models.BooleanField(_('Field is required'), default=True)
    placeholder_text = models.CharField(_('Placeholder text'), max_length=50)
    help_text = models.TextField(_('Help text'), blank=True, null=True,
                                 help_text=_('Explanatory text displayed next to input field. Just like this one.'))

    def __unicode__(self):
        return self.label


class FieldsetPlugin(CMSPlugin):

    legend = models.CharField(_('Legend'), max_length=50, blank=True)

    def __unicode__(self):
        return self.legend or str(self.pk)


class ButtonPlugin(CMSPlugin):

    label = models.CharField(_('Label'), max_length=50)

    def __unicode__(self):
        return self.label
