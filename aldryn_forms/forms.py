# -*- coding: utf-8 -*-
from django import forms


class BooleanFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text']

    def save(self, commit=True):
        self.instance.required = False
        return super(BooleanFieldForm, self).save(commit)


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'required', 'help_text']
