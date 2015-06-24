# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .models import EmailNotification, EmailNotificationFormPlugin


class EmailNotificationInline(admin.StackedInline):
    model = EmailNotification
    extra = 1
    fieldsets = [
        (
            None,
            {'fields': ['template']}
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


class EmailNotificationForm(FormPlugin):
    name = _('Email Notification Form')
    model = EmailNotificationFormPlugin
    inlines = [EmailNotificationInline]

    def send_notifications(self, instance, form):
        pass


plugin_pool.register_plugin(EmailNotificationForm)
