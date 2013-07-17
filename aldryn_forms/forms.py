# -*- coding: utf-8 -*-
from django import forms


class BooleanFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        if 'instance' not in kwargs:
            initial['required'] = False
        kwargs['initial'] = initial
        super(BooleanFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['label', 'required', 'help_text']


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'required', 'help_text']
