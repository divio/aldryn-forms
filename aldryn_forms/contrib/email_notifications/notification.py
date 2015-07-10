# -*- coding: utf-8 -*-
from django.utils.translation import ugettext


class BaseNotificationConf(object):
    # list of extra context keys available for email content/headers
    # format should be:
    # [(Title, [(field_1, field_1_label), (field_2, field_2_label)])]
    # fields have to be valid python identifiers
    custom_context_choices = None

    # should we allow the user to configure the email txt format?
    # this is not the same as the html option above
    # we can't disable txt format but we can choose to not display
    # it on the admin.
    txt_email_format_configurable = True

    # should we send out an html version of the email?
    # by design if the html version of email is enabled
    # then is configurable via the admin.
    html_email_format_enabled = True

    def __init__(self, form_plugin):
        self.form_plugin = form_plugin

    def get_context(self, form):
        text_context = form.get_cleaned_data()
        text_context['form_name'] = self.form_plugin.name

        if self.custom_context_choices:
            custom_context = self.get_custom_context(form)
            text_context.update(custom_context)
        return text_context

    def get_custom_context(self, form):
        return {}

    def get_context_keys_as_choices(self):
        choices =  [
            (
                ugettext('Fields'),
                list(self.form_plugin.get_form_fields_as_choices())
            ),
        ]

        if self.custom_context_choices:
            choices += list(self.custom_context_choices)
        return choices


class DefaultNotificationConf(BaseNotificationConf):
    html_email_format_enabled = True
    txt_email_format_configurable = True
