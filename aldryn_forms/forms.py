# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class TextFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TextFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min length')
        self.fields['min_value'].help_text = _(u'Required number of characters to type.')

        self.fields['max_value'].label = _(u'Max length')
        self.fields['max_value'].help_text = _(u'Maximum number of characters to type.')
        self.fields['max_value'].required = True

    class Meta:
        fields = ['label', 'placeholder_text', 'required', 'help_text', 'min_value', 'max_value']


class BooleanFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:  # creating new one
            initial = kwargs.pop('initial', {})
            initial['required'] = False
            kwargs['initial'] = initial
        super(BooleanFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['label', 'required', 'help_text']


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'required', 'help_text']


class MultipleSelectFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MultipleSelectFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min choices')
        self.fields['min_value'].help_text = _(u'Required amount of elements to chose.')

        self.fields['max_value'].label = _(u'Max choices')
        self.fields['max_value'].help_text = _(u'Maximum amount of elements to chose.')

    class Meta:
        fields = ['label', 'help_text', 'min_value', 'max_value']

    def clean(self):
        min_value = self.cleaned_data.get('min_value')
        max_value = self.cleaned_data.get('max_value')
        if min_value and max_value and min_value > max_value:
            self.append_to_errors('min_value', _(u'Min choices value can not be greater then max choices value.'))
        return self.cleaned_data

    def append_to_errors(self, field, message):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])
