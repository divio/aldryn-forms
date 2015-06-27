# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.core.mail import get_connection
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .models import EmailNotification, EmailNotificationFormPlugin
from .validators import is_valid_recipient


logger = logging.getLogger(__name__)


class EmailNotificationInline(admin.StackedInline):
    model = EmailNotification
    extra = 0
    fieldsets = [
        (
            None,
            {'fields': ['theme']}
        ),
        (
            None,
            {'fields': ['text_variables']}
        ),
        (
            'Recipient',
            {'fields': ['to_user', ('to_name', 'to_email')]}
        ),
        (
            'Sender',
            {'fields': [('from_name', 'from_email')]}
        ),
        (
            'Email body',
            {'fields': ['subject', 'body_text', 'body_html']}
        ),
    ]
    readonly_fields = ['text_variables']
    text_variables_help_text = _('variables can be used with "$" like $variable')

    def text_variables(self, obj):
        variables = obj.get_text_variables()
        li_items = (u'<li>{0} | {1}</li>'.format(*var) for var in variables)
        unordered_list = u'<ul>{0}</ul>'.format(u''.join(li_items))
        help_text = u'<p class="help">{0}</p>'.format(self.text_variables_help_text)
        return unordered_list + '\n' + help_text
    text_variables.allow_tags = True
    text_variables.short_description = _('available text variables')


class EmailNotificationForm(FormPlugin):
    name = _('Email Notification Form')
    model = EmailNotificationFormPlugin
    inlines = [EmailNotificationInline]

    fieldsets = [
        (
            'General options',
            {'fields': ['name', 'form_template', 'error_message', 'success_message', 'custom_classes']}
        ),
        (
            'Redirect',
            {'fields': ['redirect_type', 'page', 'url']}
        )
    ]

    def send_notifications(self, instance, form):
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
        except Exception:
            # I use a "catch all" in order to not couple this handler to a specific email backend
            # different email backends have different exceptions.
            logger.exception("Could not send notification emails.")
            return []

        form_data = form.get_cleaned_data()

        notifications = instance.email_notifications.select_related('form')

        emails = []
        recipients = []

        for notification in notifications:
            email = notification.prepare_email(form_data=form_data)

            to_email = email.to[0]

            if is_valid_recipient(to_email):
                emails.append(email)
                recipients.append(to_email)

        try:
            connection.send_messages(emails)
        except:
            # again, we catch all exceptions to be backend agnostic
            logger.exception("Could not send notification emails.")
            recipients = []
        return recipients


plugin_pool.register_plugin(EmailNotificationForm)
