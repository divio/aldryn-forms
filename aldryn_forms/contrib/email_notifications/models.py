# -*- coding: utf-8 -*-
import logging

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
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text=_('A name to identify this message. Not visible to recipients.')
    )
    theme = models.CharField(
        verbose_name=_('theme'),
        max_length=200,
        help_text=_('Provides the base theme for the email.'),
        choices=EMAIL_THEMES,
        default=DEFAULT_EMAIL_THEME,
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
        to=FormPlugin,
        related_name='email_notifications'
    )

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
