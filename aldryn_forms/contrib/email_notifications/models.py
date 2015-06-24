# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from django.conf import settings
from django.core.mail import get_connection
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from aldryn_forms.models import FormPlugin

from emailit.api import construct_mail


ADDITIONAL_EMAIL_THEMES = getattr(settings, "ALDRYN_FORMS_EMAIL_THEMES",[])
DEFAULT_EMAIL_THEME = [('default', _('default'))]
EMAIL_THEMES = DEFAULT_EMAIL_THEME + ADDITIONAL_EMAIL_THEMES

logger = logging.getLogger(__name__)


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

    def send_email_notifications(self):
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
        except Exception:
            # I use a "catch all" in order to not couple this handler to a specific email backend
            logger.exception("Could not send notification emails.")
            return 0

        notifications = self.email_notifications.select_related('form')
        emails = [notification.prepare_email() for notification in notifications]
        return connection.send_messages(emails)


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

    def get_text_variables(self):
        return list(self.form.get_fields_as_choices())

    def get_context(self):
        context = {}

        recipient_email = self.get_recipient_email()
        recipient_name = self.get_recipient_name()

        if recipient_email:
            context['to_email'] = recipient_email

        if recipient_name:
            context['to_name'] = recipient_name

        if self.from_name:
            context['from_name'] = self.from_name

        if self.from_email:
            context['from_email'] = self.from_email
        return context

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

    def prepare_email(self):
        form_plugin = self.form

        context = self.get_context()
        context['form_name'] = form_plugin.name
        context['form_plugin'] = form_plugin.form

        recipient_email = self.get_recipient_email()

        email = construct_mail(
            context=context,
            language=form_plugin.language,
            recipients=[recipient_email],
            template_base='aldryn_forms/email_notifications/emails/notification',
        )
        return email
