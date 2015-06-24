# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin

from .models import EmailNotification, EmailNotificationFormPlugin


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
        li_items = (u'<li>{} | {}</li>'.format(*var) for var in variables)
        unordered_list = u'<ul>{}</ul>'.format(u''.join(li_items))
        help_text = u'<p class="help">{}</p>'.format(self.text_variables_help_text)
        return unordered_list + '\n' + help_text
    text_variables.allow_tags = True
    text_variables.short_description = _('available text variables')


class EmailNotificationForm(FormPlugin):
    name = _('Email Notification Form')
    model = EmailNotificationFormPlugin
    inlines = [EmailNotificationInline]

    def send_notifications(self, instance, form):
        pass


plugin_pool.register_plugin(EmailNotificationForm)
