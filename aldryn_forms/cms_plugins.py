# -*- coding: utf-8 -*-
from django import forms
from django.contrib.admin import TabularInline
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_forms import models
from aldryn_forms.forms import BooleanFieldForm, SelectFieldForm


class FormElement(CMSPluginBase):

    module = _('Forms')

    def get_form_fields(self, instance):
        raise NotImplementedError()


class FieldContainer(FormElement):

    allow_children = True

    def get_form_fields(self, instance):
        form_fields = {}
        for child_plugin_instance in instance.child_plugin_instances:
            child_plugin = child_plugin_instance.get_plugin_instance()[1]
            if hasattr(child_plugin, 'get_form_fields'):
                fields = child_plugin.get_form_fields(instance=child_plugin_instance)
                form_fields.update(fields)
        return form_fields


class FormPlugin(FieldContainer):

    render_template = 'aldryn_forms/form.html'
    name = _('Form')
    model = models.FormPlugin

    def render(self, context, instance, placeholder):
        context = super(FormPlugin, self).render(context, instance, placeholder)
        if 'form' not in context:  # the context not from form processing view
            context['form'] = self.get_form_class(instance)()
        return context

    def get_form_class(self, instance):
        """
        Constructs form class basing on content's field plugin instances.
        """
        fields = self.get_form_fields(instance)
        return forms.forms.DeclarativeFieldsMetaclass('AldrynDynamicForm', (forms.Form,), fields)

    def get_success_url(self, instance):
        return reverse('send', kwargs={'pk': instance.pk})

plugin_pool.register_plugin(FormPlugin)


class Fieldset(FieldContainer):

    render_template = 'aldryn_forms/fieldset.html'
    name = _('Fieldset')
    model = models.FieldsetPlugin

plugin_pool.register_plugin(Fieldset)


class Field(FormElement):

    render_template = 'aldryn_forms/field.html'
    model = models.FieldPlugin

    def get_field_name(self, instance):
        return u'aldryn-forms-field-%d' % (instance.pk,)

    def render(self, context, instance, placeholder):
        context = super(Field, self).render(context, instance, placeholder)
        if 'form' in context:
            context['field'] = context['form'][self.get_field_name(instance)]
        return context


class TextField(Field):

    name = _('TextField')

    def get_form_fields(self, instance):
        field = forms.CharField(
            max_length=100,
            label=instance.label,
            help_text=instance.help_text,
            required=instance.required)
        if instance.placeholder_text:
            field.widget.attrs['placeholder'] = instance.placeholder_text
        return {self.get_field_name(instance): field}

plugin_pool.register_plugin(TextField)


class BooleanField(Field):

    name = _('Yes/No Field')
    form = BooleanFieldForm

    def get_form_fields(self, instance):
        field = forms.BooleanField(
            label=instance.label,
            help_text=instance.help_text,
            required=instance.required)
        return {self.get_field_name(instance): field}

plugin_pool.register_plugin(BooleanField)


class SelectOptionInline(TabularInline):

    model = models.Option


class SelectField(Field):

    name = _('Select Field')
    form = SelectFieldForm
    inlines = [SelectOptionInline]

    def get_form_fields(self, instance):
        field = forms.ModelChoiceField(
            queryset=instance.option_set.all(),
            label=instance.label,
            help_text=instance.help_text,
            required=instance.required)
        return {self.get_field_name(instance): field}

plugin_pool.register_plugin(SelectField)


class MultipleSelectField(SelectField):

    name = _('Multiple Select Field')

    def get_form_fields(self, instance):
        field = forms.ModelMultipleChoiceField(
            queryset=instance.option_set.all(),
            label=instance.label,
            help_text=instance.help_text,
            required=instance.required,
            widget=forms.CheckboxSelectMultiple)
        return {self.get_field_name(instance): field}

plugin_pool.register_plugin(MultipleSelectField)


class SubmitButton(FormElement):

    render_template = 'aldryn_forms/submit_button.html'
    name = _('Submit Button')
    model = models.ButtonPlugin

    def get_form_fields(self, instance):
        return {}

plugin_pool.register_plugin(SubmitButton)
