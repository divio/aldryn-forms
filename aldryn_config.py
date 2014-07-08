# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    show_all_recipients = forms.CheckboxField('Show all users in form recipients select', required=False)

    def to_settings(self, data, settings):
        settings['ALDRYN_FORMS_SHOW_ALL_RECIPIENTS'] = data['show_all_recipients']
        return settings
