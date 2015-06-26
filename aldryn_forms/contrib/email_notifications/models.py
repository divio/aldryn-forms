# -*- coding: utf-8 -*-
from collections import defaultdict
from functools import partial
from email.utils import formataddr

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from aldryn_forms.models import FormPlugin

from emailit.api import construct_mail

from .helpers import render_text


ADDITIONAL_EMAIL_THEMES = getattr(settings, "ALDRYN_FORMS_EMAIL_THEMES", [])
DEFAULT_EMAIL_THEME = getattr(
    settings,
    "ALDRYN_FORMS_EMAIL_DEFAULT_THEME",
    [('default', _('default'))]
)
EMAIL_THEMES = DEFAULT_EMAIL_THEME + ADDITIONAL_EMAIL_THEMES


class EmailNotificationFormPlugin(FormPlugin):

    class Meta:
        proxy = True

    def copy_relations(self, oldinstance):
        for item in oldinstance.email_notifications.all():
            item.pk = None
            item.form = self
            item.save()

    def get_fields_as_choices(self):
        fields = self.get_form_fields()
        occurrences = defaultdict(int)

        for field in fields:
            field_type = field.field_type
            occurrences[field_type] += 1
            occurrence = occurrences[field_type]

            field_key = u'{}_{}'.format(field_type, occurrence)

            if field.label:
                label = field.label
            else:
                # get the name defined for this plugin class in cms_plugins.py
                plugin_name = unicode(field.get_plugin_class().name)
                # label becomes "Plugin name #1"
                label = u'{} #{}'.format(plugin_name, occurrence)

            yield (field_key, label)


class EmailNotification(models.Model):
    theme = models.CharField(
        verbose_name=_('theme'),
        max_length=200,
        help_text=_('Provides the base theme for the email.'),
        choices=EMAIL_THEMES
    )
    to_name = models.CharField(
        verbose_name=_('to name'),
        max_length=200,
        blank=True
    )
    to_email = models.EmailField(
        verbose_name=_('to email'),
        blank=True
    )
    to_user = models.ForeignKey(
        to=getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        verbose_name=_('to user'),
        blank=True,
        null=True,
        limit_choices_to={'is_staff': True},
    )
    from_name = models.CharField(
        verbose_name=_('from name'),
        max_length=200,
        blank=True
    )
    from_email = models.EmailField(
        verbose_name=_('from email'),
        blank=True
    )
    subject = models.CharField(
        verbose_name=_("subject"),
        max_length=200,
    )
    body_text = models.TextField(blank=True)
    body_html = HTMLField(blank=True)
    form = models.ForeignKey(
        to=EmailNotificationFormPlugin,
        related_name='email_notifications'
    )

    def __unicode__(self):
        to_name = self.get_recipient_name()
        to_email = self.get_recipient_email()
        return u'{} ({})'.format(to_name, to_email)

    def clean(self):
        recipient_email = self.get_recipient_email()

        if not recipient_email:
            message = ugettext('Please provide a recipient.')
            raise ValidationError(message)

    def get_text_variables(self):
        return list(self.form.get_fields_as_choices())

    def get_recipient_name(self):
        if self.to_name:
            # manual name takes precedence over user relationship.
            name = self.to_name
        elif self.to_user_id:
            name = self.to_user.get_full_name()
        else:
            name = ''
        return name

    def get_recipient_email(self):
        if self.to_email:
            # manual email takes precedence over user relationship.
            email = self.to_email
        elif self.to_user_id:
            email = self.to_user.email
        else:
            email = ''
        return email

    def get_email_context(self, form_data):
        context = {
            'data': form_data,
            'form_plugin': self.form,
            'form_name': self.form.name,
            'email_notification': self,
        }
        context.update(form_data)
        return context

    def get_email_kwargs(self, form_data):
        context = self.get_email_context(form_data)

        kwargs = {
            'context': context,
            'language': self.form.language,
            'template_base': 'aldryn_forms/email_notifications/emails/notification'
        }
        render = partial(render_text, context=context)

        recipient_name = self.get_recipient_name()

        recipient_email = self.get_recipient_email()
        recipient_email = render(recipient_email)

        if recipient_name:
            recipient_name = render(recipient_name)
            recipient_email = formataddr((recipient_name, recipient_email))

        kwargs['recipients'] = [recipient_email]

        if self.from_email:
            from_email = render(self.from_email)

            if self.from_name:
                from_name = render(self.from_name)
                from_email = formataddr((from_name, from_email))

            kwargs['from_email'] = from_email
        return kwargs

    def prepare_email(self, form_data):
        email_kwargs = self.get_email_kwargs(form_data)
        email = construct_mail(**email_kwargs)
        return email

    def render_body_text(self, context):
        return render_text(self.body_text, context)

    def render_body_html(self, context):
        return render_text(self.body_html, context)

    def render_subject(self, context):
        return render_text(self.subject, context)
