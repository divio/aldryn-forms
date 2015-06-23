# -*- coding: utf-8 -*-
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


class EmailTemplate(TranslatableModel):
    allowed_context_variables = [
        'first_name',
        'last_name',
        'full_name',
        'form_name',
        'form_data_html',
        'form_data_text',
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

    def render_message(self, message, context):
        context = {key: context.get(key, '') for key in self.allowed_context_variables}
        template = Template(template=message)
        return template.safe_substitute(**context)

    def render_text_message(self, context):
        return self.render_message(self.email_body_text, context)

    def render_html_message(self, context):
        return self.render_message(self.email_body_html, context)

    def send_emails(self, context, recipients, language=None):
        context['form_email_template'] = self

        try:
            connection = get_connection(fail_silently=False)
            connection.open()
        except Exception:
            # I use a "catch all" in order to not couple this handler to a specific email backend
            logger.error("Could not send notification emails.", exc_info=True)
            return 0

        def prepare_email(recipient):
            local_context = {
                'first_name': recipient.first_name,
                'last_name': recipient.last_name,
                'full_name': recipient.get_full_name(),
                # rendered field/value pairs for both html and text versions
                'form_data_html': render_to_string('aldryn_forms/emails/includes/form_data.html', context),
                'form_data_text': render_to_string('aldryn_forms/emails/includes/form_data.txt', context),
            }
            local_context.update(context)

            email = construct_mail(
                context=local_context,
                language=language,
                recipients=[recipient.email],
                template_base='aldryn_forms/emails/notification',
            )
            return email

        emails = [prepare_email(recipient) for recipient in recipients]
        return connection.send_messages(emails)

    def clean(self):
        context = {key: 'test' for key in self.allowed_context_variables}

        try:
            self.render_text_message(context=context)
            self.render_html_message(context=context)
        except Exception, e:
            raise ValidationError(str(e))


class EmailNotificationFormPlugin(FormPlugin):
    email_notification_template = models.ForeignKey(
        to=EmailTemplate,
        verbose_name=_('template'),
        help_text=_('Template is rendered when sending the user '
                    'an email notification for this form'),
        blank=True,
        null=True
    )
    email_notification_to_email = models.EmailField(blank=True)
    email_notification_to_name = models.CharField(max_length=200, blank=True)
    email_notification_from_name = models.CharField(max_length=200, blank=True)
    email_notification_from_email = models.EmailField(blank=True)
    email_notification_subject = models.CharField(
        verbose_name=_("subject"),
        max_length=200,
        blank=True
    )
    email_notification_body_text = models.TextField(blank=True)
    email_notification_body_html = models.TextField(blank=True)

    def send_staff_notification_email(self, form, form_plugin):
        recipients = self.people_notified.exclude(email='')

        context = {
            'form_name': form_plugin.name,
            'form_data': list(form_data),
            'form_plugin': form_plugin,
            'subject': form_plugin.email_notification_subject,
        }

        template = form_plugin.email_notification_template
        template.send_emails(
            context,
            recipients=recipients,
            language=form_plugin.language,
        )
