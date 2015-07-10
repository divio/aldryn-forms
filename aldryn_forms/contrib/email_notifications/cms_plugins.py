# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.core.mail import get_connection
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin
from aldryn_forms.validators import is_valid_recipient

from .notification import DefaultNotificationConf
from .models import EmailNotification, EmailNotificationFormPlugin


logger = logging.getLogger(__name__)


class NewEmailNotificationInline(admin.StackedInline):
    extra = 1
    fields = ['theme']
    model = EmailNotification
    verbose_name = _('new email notification')
    verbose_name_plural = _('new email notifications')

    def get_queryset(self, request):
        queryset = super(NewEmailNotificationInline, self).get_queryset(request)
        return queryset.none()


class ExistingEmailNotificationInline(admin.StackedInline):
    model = EmailNotification
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
    ]

    readonly_fields = ['text_variables']
    text_variables_help_text = _('variables can be used with by '
                                 'wrapping with "${variable}" like ${variable}')

    def has_add_permission(self, request):
        return False

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ExistingEmailNotificationInline, self).get_fieldsets(request, obj)

        if obj is None:
            return fieldsets

        email_fieldset = self.get_email_fieldset(obj)
        fieldsets = list(fieldsets) + email_fieldset
        return fieldsets

    def get_email_fieldset(self, obj):
        fields = ['subject']

        notification_conf = obj.get_notification_conf()

        if notification_conf.txt_email_format_configurable:
            # add the body_text field only if it's configurable
            fields.append('body_text')

        if notification_conf.html_email_format_enabled:
            # add the body_html field only if email is allowed
            # to be sent in html version.
            fields.append('body_html')
        return [('Email', {'fields': fields})]

    def text_variables(self, obj):
        if obj.pk is None:
            return ''

        # list of tuples - [('category', [('value', 'label')])]
        choices_by_category = obj.form.get_notification_text_context_keys_as_choices()

        li_items = []

        for category, choices in choices_by_category:
            # <li>field_1</li><li>field_2</li>
            fields_li = u''.join((u'<li>{0} | {1}</li>'.format(*var) for var in choices))

            if fields_li:
                li_item = u'<li>{0}</li><ul>{1}</ul>'.format(category, fields_li)
                li_items.append(li_item)
        unordered_list = u'<ul>{0}</ul>'.format(u''.join(li_items))
        help_text = u'<p class="help">{0}</p>'.format(self.text_variables_help_text)
        return unordered_list + u'\n' + help_text
    text_variables.allow_tags = True
    text_variables.short_description = _('available text variables')


class EmailNotificationForm(FormPlugin):
    name = _('Email Notification Form')
    model = EmailNotificationFormPlugin
    inlines = [
        ExistingEmailNotificationInline,
        NewEmailNotificationInline
    ]
    notification_conf_class = DefaultNotificationConf

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

    def get_inline_instances(self, request, obj=None):
        inlines = super(EmailNotificationForm, self).get_inline_instances(request, obj)

        if obj is None:
            # remove ExistingEmailNotificationInline inline instance
            # if we're first creating this object.
            inlines = [inline for inline in inlines
                       if not isinstance(inline, ExistingEmailNotificationInline)]
        return inlines

    def send_notifications(self, instance, form):
        try:
            connection = get_connection(fail_silently=False)
            connection.open()
        except:
            # I use a "catch all" in order to not couple this handler to a specific email backend
            # different email backends have different exceptions.
            logger.exception("Could not send notification emails.")
            return []

        notifications = instance.email_notifications.select_related('form')

        emails = []
        recipients = []

        for notification in notifications:
            email = notification.prepare_email(form=form)

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
