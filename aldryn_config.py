# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):

    public_key = forms.CharField('Re-captcha public key', max_length=40, required=False)
    private_key = forms.CharField('Re-captcha private key', max_length=40, required=False)
    show_all_recipients = forms.CheckboxField('Show all users in form recipients select', default=False, required=False)

    def to_settings(self, data, settings):
        settings['RECAPTCHA_PUBLIC_KEY'] = data['public_key']
        settings['RECAPTCHA_PRIVATE_KEY'] = data['private_key']
        settings['ALDRYN_FORMS_SHOW_ALL_RECIPIENTS'] = data['show_all_recipients']
        return settings
