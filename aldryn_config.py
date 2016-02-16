# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    show_all_recipients = forms.CheckboxField('Include only admin users as selectable e-mail recipients instead of everyone.', required=False)

    def to_settings(self, data, settings):
        settings['ALDRYN_FORMS_SHOW_ALL_RECIPIENTS'] = not data['show_all_recipients']
        return settings
