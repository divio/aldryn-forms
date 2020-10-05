import logging
from email.utils import parseaddr
from typing import List

from django.contrib import admin
from django.core.mail import get_connection
from django.template.defaultfilters import safe
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool

from aldryn_forms.cms_plugins import FormPlugin
from aldryn_forms.validators import is_valid_recipient

from .models import EmailNotification, EmailNotificationFormPlugin
from .notification import DefaultNotificationConf


logger = logging.getLogger(__name__)


class NewEmailNotificationInline(admin.StackedInline):
    extra = 1
    fields = ['theme']
    model = EmailNotification
    verbose_name = _('new email notification')
    verbose_name_plural = _('new email notifications')

    fieldsets = (
        (None, {
            'fields': (
                'theme',
            )
        }),
    )

    def get_queryset(self, request):
        queryset = super(NewEmailNotificationInline, self).get_queryset(request)
        return queryset.none()


class ExistingEmailNotificationInline(admin.StackedInline):
    model = EmailNotification

    fieldsets = (
        (None, {
            'fields': (
                'theme',
            )
        }),
        (_('Recipients'), {
            'fields': (
                'text_variables',
                'to_user',
                ('to_name', 'to_email'),
                ('from_name', 'from_email'),
                'reply_to_email',
            )
        }),
    )

    readonly_fields = ['text_variables']

    text_variables_help_text = _(
        'the variables can be used within the email body, email sender,'
        'and other notification fields'
    )

    def has_add_permission(self, request, obj=None):
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
        return [(_('Email'), {
            'classes': ('collapse',),
            'fields': fields
        })]

    def text_variables(self, obj: EmailNotification) -> str:
        if obj.pk is None:
            return ''

        # list of tuples - [('category', [('value', 'label')])]
        choices_by_category = obj.form.get_notification_text_context_keys_as_choices()

        var_items: List[str] = []
        for category, choices in choices_by_category:
            for choice_tuple in choices:
                field_value = choice_tuple[0]
                var_items += '<li>${' + field_value + '}</li>'

        vars_html_list = f'<p>{"".join(var_items)}</p>'
        help_text = (
            f'<p class="help">'
            f'{_("the variables can be used within the email body, email sender, and other notification fields")}'
            f'</p>'
        )
        return safe(vars_html_list + u'\n' + help_text)
    text_variables.allow_tags = True
    text_variables.short_description = _('available text variables')

    class Media:
        css = {
            'all': ['email_notifications/admin/email-notifications.css']
        }


class EmailNotificationForm(FormPlugin):
    name = _('Form')
    model = EmailNotificationFormPlugin
    inlines = [
        ExistingEmailNotificationInline,
        NewEmailNotificationInline
    ]
    notification_conf_class = DefaultNotificationConf
    child_ckeditor_body_css_class = 'aldryn-forms-form-plugin'

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'redirect_type',
                ('redirect_page', 'url'),
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'is_enable_autofill_from_url_params',
                'form_template',
                'error_message',
                'success_message',
                'custom_classes',
                'action_backend',
            )
        }),
    )

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
        except:  # noqa
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
                recipients.append(parseaddr(to_email))

        try:
            connection.send_messages(emails)
        except:  # noqa
            # again, we catch all exceptions to be backend agnostic
            logger.exception("Could not send notification emails.")
            recipients = []
        return recipients


plugin_pool.register_plugin(EmailNotificationForm)
