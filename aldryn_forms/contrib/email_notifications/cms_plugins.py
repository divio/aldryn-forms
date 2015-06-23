# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .models import EmailNotification, EmailNotificationFormPlugin


class EmailNotificationInline(admin.StackedInline):
    model = EmailNotification
    extra = 1
    add_fieldsets = [(None, {'fields': ['template']})]
    edit_fieldsets = [
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

    def get_fieldsets(self, request, obj=None):
        if obj and obj.pk:
            return self.edit_fieldsets
        else:
            return self.add_fieldsets

    def get_readonly_fields(self, request, obj=None):
        fields = super(EmailNotificationInline, self).get_readonly_fields(request, obj)

        if obj and obj.pk:
            # changing the template of an existing notification shouldn't be allowed.
            # this is because the notification copies the text in the template
            # so if template changes then they're completely out of sync.
            fields += ['template']
        return fields


class EmailNotificationForm(FormPlugin):
    name = _('Email Notification Form')
    model = EmailNotificationFormPlugin
    inlines = [EmailNotificationInline]


plugin_pool.register_plugin(EmailNotificationForm)
