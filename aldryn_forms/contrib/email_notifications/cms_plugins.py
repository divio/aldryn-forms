# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.core.mail import get_connection
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .models import EmailNotification, EmailNotificationFormPlugin


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

    def send_notifications(self, instance, form):
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
        except Exception:
            # I use a "catch all" in order to not couple this handler to a specific email backend
            # different email backends have different exceptions.
            logger.exception("Could not send notification emails.")
            return 0

        form_data = form.get_cleaned_data()

        notifications = instance.email_notifications.select_related('form')

        emails = [notification.prepare_email(form_data=form_data)
                  for notification in notifications]

        recipients = [email.to[0] for email in emails if email.to]
        return recipients


plugin_pool.register_plugin(EmailNotificationForm)
