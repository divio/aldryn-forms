# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.admin import TabularInline
from django.core.validators import MinLengthValidator
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_forms import models
from .forms import (
    FormPluginForm,
    TextFieldForm,
    TextAreaFieldForm,
    BooleanFieldForm,
    MultipleSelectFieldForm,
    SelectFieldForm,
    CaptchaFieldForm,
    RadioFieldForm,
)
from .validators import MinChoicesValidator, MaxChoicesValidator
from .views import SendView


class FormElement(CMSPluginBase):
    # Don't cache anything.
    cache = False
    module = _('Forms')

    def get_form_fields(self, instance):
        raise NotImplementedError()


class FieldContainer(FormElement):
    allow_children = True

    def get_form_fields(self, instance):
        form_fields = {}
        for child_plugin_instance in instance.child_plugin_instances:
            plugin_instance, child_plugin = child_plugin_instance.get_plugin_instance()
            if plugin_instance and hasattr(child_plugin, 'get_form_fields'):
                fields = child_plugin.get_form_fields(instance=plugin_instance)
                form_fields.update(fields)
        return form_fields


class FormPlugin(FieldContainer):
    render_template = 'aldryn_forms/form.html'
    name = _('Form')
    model = models.FormPlugin
    form = FormPluginForm
    filter_horizontal = ['recipients']

    fieldsets = [
        (
            'General options',
            {'fields': ['name', 'error_message', 'recipients', 'custom_classes']}
        ),
        (
            'Redirect',
            {'fields': ['redirect_type', 'page', 'url']}
        )
    ]

    def render(self, context, instance, placeholder):
        context = super(FormPlugin, self).render(context, instance, placeholder)
        if 'form' not in context:  # the context not from form processing view
            template_response = SendView.as_view(
                template_name=self.render_template
            )(request=context['request'], pk=instance.pk)
            context.update(template_response.context_data)
        return context

    def get_form_class(self, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = self.get_form_fields(instance)
        return forms.forms.DeclarativeFieldsMetaclass('AldrynDynamicForm', (forms.Form,), fields)

    def get_success_url(self, instance):
        if instance.redirect_type == models.FormPlugin.REDIRECT_TO_PAGE:
            return instance.page.get_absolute_url()
        elif instance.redirect_type == models.FormPlugin.REDIRECT_TO_URL:
            return instance.url
        else:
            raise RuntimeError('Form is not configured properly.')

plugin_pool.register_plugin(FormPlugin)


class Fieldset(FieldContainer):
    render_template = 'aldryn_forms/fieldset.html'
    name = _('Fieldset')
    model = models.FieldsetPlugin

plugin_pool.register_plugin(Fieldset)


class Field(FormElement):
    render_template = 'aldryn_forms/field.html'
    model = models.FieldPlugin

    # Custom field related attributes
    form_field = None
    form_field_widget = None
    form_field_enabled_options = ['label', 'help_text', 'required']
    form_field_disabled_options = []

    def get_field_name(self, instance):
        return u'aldryn-forms-field-%d' % (instance.pk,)

    def get_form_fields(self, instance):
        return {self.get_field_name(instance=instance): self.get_form_field(instance=instance)}

    def get_form_field(self, instance):
        form_field_class = self.get_form_field_class(instance)
        form_field_kwargs = self.get_form_field_kwargs(instance)
        return form_field_class(**form_field_kwargs)

    def get_form_field_class(self, instance):
        return self.form_field

    def get_form_field_kwargs(self, instance):
        allowed_options = self.get_field_enabled_options()

        kwargs = {'widget': self.get_form_field_widget(instance)}

        if 'error_messages' in allowed_options:
            kwargs['error_messages'] = self.get_error_messages(instance=instance)
        if 'label' in allowed_options:
            kwargs['label'] = instance.label
        if 'help_text' in allowed_options:
            kwargs['help_text'] = instance.help_text
        if 'max_length' in allowed_options:
            kwargs['max_length'] = instance.max_value
        if 'required' in allowed_options:
            kwargs['required'] = instance.required
        if 'validators' in allowed_options:
            kwargs['validators'] = self.get_form_field_validators(instance)
        if 'default_value' in allowed_options:
            qs = instance.option_set.filter(default_value=True)
            kwargs['initial'] = qs[0] if qs.exists() else None

        return kwargs

    def get_form_field_widget(self, instance):
        form_field_widget_class = self.get_form_field_widget_class(instance)
        form_field_widget_kwargs = self.get_form_field_widget_kwargs(instance)
        form_field_widget_kwargs['attrs'] = self.get_form_field_widget_attrs(instance)
        return form_field_widget_class(**form_field_widget_kwargs)

    def get_form_field_widget_class(self, instance):
        return self.form_field_widget

    def get_form_field_widget_attrs(self, instance):
        attrs = {}
        if instance.placeholder_text:
            attrs['placeholder'] = instance.placeholder_text
        if instance.custom_classes:
            attrs['class'] = instance.custom_classes
        return attrs

    def get_form_field_widget_kwargs(self, instance):
        return {}

    def render(self, context, instance, placeholder):
        context = super(Field, self).render(context, instance, placeholder)
        if 'form' in context:
            context['field'] = context['form'][self.get_field_name(instance=instance)]
        return context

    def get_fieldsets(self, request, obj=None):
        if self.form:
            fields = set(self.form._meta.fields)
        else:
            fields = ['label']

        in_fields = lambda x: x in fields

        general_fields = filter(in_fields, ['label', 'placeholder_text', 'help_text'])
        fieldsets = [
            (_('General options'), {'fields': general_fields}),
        ]

        boundries_fields = filter(in_fields, ['min_value', 'max_value'])
        if boundries_fields:
            fieldsets.append(
                (_('Min and max values'), {'fields': boundries_fields}))

        required_fields = filter(in_fields, ['required', 'required_message'])
        if required_fields:
            fieldsets.append(
                (_('Required'), {'fields': required_fields}))

        extra_fields = filter(in_fields, ['custom_classes', 'text_area_columns', 'text_area_rows'])
        if extra_fields:
            fieldsets.append(
                (_('Extra'), {'fields': extra_fields}))

        return fieldsets

    def get_error_messages(self, instance):
        if instance.required_message:
            return {'required': instance.required_message}
        else:
            return None

    def get_form_field_validators(self, instance):
        return []

    def get_field_enabled_options(self):
        enabled_options = self.form_field_enabled_options
        disabled_options = self.form_field_disabled_options
        return [option for option in enabled_options if option not in disabled_options]


class TextField(Field):
    name = _('Text Field')
    form = TextFieldForm
    form_field = forms.CharField
    form_field_widget = forms.CharField.widget
    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'max_length',
        'error_messages',
        'validators',
        'placeholder',
    ]

    def get_form_field_validators(self, instance):
        validators = []
        if instance.min_value:
            validators.append(MinLengthValidator(instance.min_value))
        return validators

plugin_pool.register_plugin(TextField)


class TextAreaField(TextField):
    name = _('Text Area Field')
    model = models.TextAreaFieldPlugin
    form = TextAreaFieldForm
    form_field_widget = forms.Textarea

    def get_form_field_widget(self, instance):
        widget = super(TextAreaField, self).get_form_field_widget(instance)

        # django adds the cols and rows attributes by default.
        # remove them if the user did not specify a value for them.
        if not instance.text_area_columns:
            del widget.attrs['cols']

        if not instance.text_area_rows:
            del widget.attrs['rows']
        return widget

    def get_form_field_widget_attrs(self, instance):
        attrs = super(TextAreaField, self).get_form_field_widget_attrs(instance)

        if instance.text_area_columns:
            attrs['cols'] = instance.text_area_columns
        if instance.text_area_rows:
            attrs['rows'] = instance.text_area_rows
        return attrs


plugin_pool.register_plugin(TextAreaField)


class BooleanField(Field):
    name = _('Yes/No Field')
    form = BooleanFieldForm
    form_field = forms.BooleanField
    form_field_widget = form_field.widget
    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'error_messages',
    ]


plugin_pool.register_plugin(BooleanField)


class SelectOptionInline(TabularInline):
    model = models.Option


class SelectField(Field):
    name = _('Select Field')
    form = SelectFieldForm
    form_field = forms.ModelChoiceField
    form_field_widget = form_field.widget
    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'error_messages',
        'default_value',
    ]
    inlines = [SelectOptionInline]

    def get_form_field_kwargs(self, instance):
        kwargs = super(SelectField, self).get_form_field_kwargs(instance)
        kwargs['queryset'] = instance.option_set.all()
        return kwargs

plugin_pool.register_plugin(SelectField)


class MultipleSelectField(SelectField):
    name = _('Multiple Select Field')
    form = MultipleSelectFieldForm
    form_field = forms.ModelMultipleChoiceField
    form_field_widget = forms.CheckboxSelectMultiple
    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'validators',
    ]

    def get_form_field_validators(self, instance):
        validators = []
        if instance.min_value:
            validators.append(MinChoicesValidator(limit_value=instance.min_value))
        if instance.max_value:
            validators.append(MaxChoicesValidator(limit_value=instance.max_value))
        return validators

    def get_form_field_kwargs(self, instance):
        kwargs = super(MultipleSelectField, self).get_form_field_kwargs(instance)
        if hasattr(instance, 'min_value') and instance.min_value == 0:
            kwargs['required'] = False
        return kwargs

plugin_pool.register_plugin(MultipleSelectField)


class RadioSelectField(Field):
    name = _('Radio Select Field')
    form = RadioFieldForm
    form_field = forms.ModelChoiceField
    form_field_widget = forms.RadioSelect

    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'error_messages',
        'default_value',
    ]
    inlines = [SelectOptionInline]

    def get_form_field_kwargs(self, instance):
        kwargs = super(RadioSelectField, self).get_form_field_kwargs(instance)
        kwargs['queryset'] = instance.option_set.all()
        kwargs['empty_label'] = None
        return kwargs

plugin_pool.register_plugin(RadioSelectField)

try:
    from captcha.fields import ReCaptchaField
    from captcha.widgets import ReCaptcha
except ImportError:
    pass
else:
    # Don't like doing this. But we shouldn't force recaptcha.
    class CaptchaField(Field):
        name = _('Captcha Field')
        form = CaptchaFieldForm
        form_field = ReCaptchaField
        form_field_widget = ReCaptcha
        form_field_enabled_options = ['label', 'error_messages']

    if getattr(settings, 'RECAPTCHA_PUBLIC_KEY', None) and getattr(settings, 'RECAPTCHA_PRIVATE_KEY', None):
        plugin_pool.register_plugin(CaptchaField)


class SubmitButton(FormElement):
    render_template = 'aldryn_forms/submit_button.html'
    name = _('Submit Button')
    model = models.ButtonPlugin

    def get_form_fields(self, instance):
        return {}

plugin_pool.register_plugin(SubmitButton)
