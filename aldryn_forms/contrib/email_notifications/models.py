# -*- coding: utf-8 -*-
import logging
from string import Template

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import get_connection
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields

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
    template = models.ForeignKey(
        to='EmailNotificationTemplate',
        verbose_name=_('template'),
        help_text=_('Template is rendered when sending the user '
                    'an email notification for this form')
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

    def save(self, **kwargs):
        if self.pk is None:
            # copy over the template values when object is first saved.
            self.body_text = self.template.get_email_body_text()
            self.body_html = self.template.get_email_body_html()
        super(EmailNotification, self).save(**kwargs)

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


class EmailNotificationTemplate(TranslatableModel):
    builtin_context_variables = [
        'form_name',
    ]

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
    translations = TranslatedFields(
        email_body_text=models.TextField(verbose_name=_("body (text)")),
        email_body_html=HTMLField(verbose_name=_("body (html)")),
    )

    def __unicode__(self):
        return self.name

    def get_email_body_text(self):
        text = self.safe_translation_getter(
            field='email_body_text',
            default='',
            any_language=False
        )
        return text

    def get_email_body_html(self):
        html = self.safe_translation_getter(
            field='email_body_html',
            default='',
            any_language=False
        )
        return html

    def render_message(self, message, context):
        return Template(template=message).safe_substitute(**context)

    def render_text_message(self, context):
        email_body_text = self.get_email_body_text()
        return self.render_message(email_body_text, context)

    def render_html_message(self, context):
        email_body_html = self.get_email_body_html()
        return self.render_message(email_body_html, context)

