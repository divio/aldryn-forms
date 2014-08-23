# -*- coding: utf-8 -*-
from django import forms
from django.contrib import messages
from django.contrib.admin import TabularInline
from django.core.validators import MinLengthValidator
from django.template.loader import select_template
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from emailit.api import send_mail

from aldryn_forms import models
from .forms import (
    EmailFieldForm,
    FormDataBaseForm,
    FormPluginForm,
    TextFieldForm,
    TextAreaFieldForm,
    BooleanFieldForm,
    MultipleSelectFieldForm,
    SelectFieldForm,
    CaptchaFieldForm,
    RadioFieldForm,
)
from .utils import get_nested_plugins, get_form_render_data
from .validators import MinChoicesValidator, MaxChoicesValidator


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
        for child_plugin_instance in get_nested_plugins(instance):
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
        request = context['request']
        form = self.process_form(instance, request)
        if form.is_valid():
            context['form_success_url'] = self.get_success_url(instance)
        context['form'] = form
        return context

    def form_valid(self, instance, request, form):
        form.save()
        message = ugettext('The form has been sent.')
        messages.success(request, message)

    def form_invalid(self, instance, request, form):
        if instance.error_message:
            form._add_error(message=instance.error_message)

    def process_form(self, instance, request):
        form_class = self.get_form_class(instance)
        form_kwargs = self.get_form_kwargs(instance, request)
        form = form_class(**form_kwargs)

        if form.is_valid():
            fields = [field for field in form.base_fields.values() if hasattr(field, '_plugin_instance')]

            # pre save field hooks
            for field in fields:
                field._plugin_instance.form_pre_save(instance=field._model_instance, form=form)

            self.form_valid(instance, request, form)

            # post save field hooks
            for field in fields:
                field._plugin_instance.form_post_save(instance=field._model_instance, form=form)
        elif request.method == 'POST':
            # only call form_invalid if request is POST and form is not valid
            self.form_invalid(instance, request, form)
        return form

    def get_form_class(self, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = self.get_form_fields(instance)
        return forms.forms.DeclarativeFieldsMetaclass('AldrynDynamicForm', (FormDataBaseForm,), fields)

    def get_form_kwargs(self, instance, request):
        kwargs = {'form_plugin': instance}

        if request.method in ('POST', 'PUT'):
            data = request.POST.copy()
            data['form_plugin_id'] = instance.pk
            kwargs['data'] = data
            kwargs['files'] = request.FILES
        return kwargs

    def get_success_url(self, instance):
        if instance.redirect_type == models.FormPlugin.REDIRECT_TO_PAGE:
            return instance.page.get_absolute_url()
        elif instance.redirect_type == models.FormPlugin.REDIRECT_TO_URL:
            return instance.url
        else:
            raise RuntimeError('Form is not configured properly.')


class Fieldset(FieldContainer):
    render_template = 'aldryn_forms/fieldset.html'
    name = _('Fieldset')
    model = models.FieldsetPlugin


class Field(FormElement):
    # template name is calculated based on field
    render_template = True
    model = models.FieldPlugin

    # Custom field related attributes
    form_field = None
    form_field_widget = None
    form_field_enabled_options = ['label', 'help_text', 'required']
    form_field_disabled_options = []

    # Used to configure default fieldset in admin form
    fieldset_general_fields = ['label', 'placeholder_text', 'help_text']
    fieldset_boundaries_fields = ['min_value', 'max_value']
    fieldset_required_conf_fields = ['required', 'required_message']
    fieldset_extra_fields = ['custom_classes', 'text_area_columns', 'text_area_rows']

    def get_field_name(self, instance):
        return u'aldryn-forms-field-%d' % (instance.pk,)

    def get_form_fields(self, instance):
        return {self.get_field_name(instance=instance): self.get_form_field(instance=instance)}

    def get_form_field(self, instance):
        form_field_class = self.get_form_field_class(instance)
        form_field_kwargs = self.get_form_field_kwargs(instance)
        field = form_field_class(**form_field_kwargs)
        # allow fields access to their model plugin class instance
        field._model_instance = instance
        # and also to the plugin class instance
        field._plugin_instance = self
        return field

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
        templates = self.get_template_names(instance)
        self.render_template = select_template(templates)
        context = super(Field, self).render(context, instance, placeholder)
        form = context.get('form')
        if form:
            field_name = self.get_field_name(instance=instance)
            context['field'] = form[field_name]
        return context

    def get_fieldsets(self, request, obj=None):
        if self.declared_fieldsets:
            return self.declared_fieldsets

        if self.form:
            fields = set(self.form._meta.fields)
        else:
            fields = ['label']

        in_fields = lambda x: x in fields

        general_fields = filter(in_fields, self.fieldset_general_fields)
        fieldsets = [
            (_('General options'), {'fields': general_fields}),
        ]

        boundries_fields = filter(in_fields, self.fieldset_boundaries_fields)
        if boundries_fields:
            fieldsets.append(
                (_('Min and max values'), {'fields': boundries_fields}))

        required_fields = filter(in_fields, self.fieldset_required_conf_fields)
        if required_fields:
            fieldsets.append(
                (_('Required'), {'fields': required_fields}))

        extra_fields = filter(in_fields, self.fieldset_extra_fields)
        if extra_fields:
            fieldsets.append(
                (_('Extra'), {'fields': extra_fields}))

        return fieldsets

    def get_error_messages(self, instance):
        if instance.required_message:
            return {'required': instance.required_message}
        else:
            return {}

    def get_form_field_validators(self, instance):
        return []

    def get_field_enabled_options(self):
        enabled_options = self.form_field_enabled_options
        disabled_options = self.form_field_disabled_options
        return [option for option in enabled_options if option not in disabled_options]

    def get_template_names(self, instance):
        template_names = [
            'aldryn_forms/fields/{0}.html'.format(instance.field_type),
            'aldryn_forms/field.html',
        ]
        return template_names

    # hooks to allow processing of form data per field
    def form_pre_save(self, instance, form):
        pass

    def form_post_save(self, instance, form):
        pass


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


class EmailField(TextField):
    name = _('Email Field')
    model = models.EmailFieldPlugin
    form = EmailFieldForm
    form_field = forms.EmailField
    fieldset_general_fields = Field.fieldset_general_fields + ['email_send_notification']
    email_template_base = 'aldryn_forms/emails/user/notification'

    def send_notification_email(self, email, form):
        context = {
            'form_name': form.instance.name,
            'form_data': get_form_render_data(form)
        }
        send_mail(
            recipients=[email],
            context=context,
            template_base=self.email_template_base
        )

    def form_post_save(self, instance, form):
        field_name = self.get_field_name(instance)
        email = form.cleaned_data.get(field_name)

        if email and instance.email_send_notification:
            self.send_notification_email(email, form)


class BooleanField(Field):
    # checkbox field
    # I add the above because searching for "checkbox" should give me this plugin :)
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


try:
    from captcha.fields import CaptchaField, CaptchaTextInput
except ImportError:
    pass
else:
    # Don't like doing this. But we shouldn't force captcha.
    class CaptchaField(Field):
        name = _('Captcha Field')
        form = CaptchaFieldForm
        form_field = CaptchaField
        form_field_widget = CaptchaTextInput
        form_field_enabled_options = ['label', 'error_messages']

    plugin_pool.register_plugin(CaptchaField)


class SubmitButton(FormElement):
    render_template = 'aldryn_forms/submit_button.html'
    name = _('Submit Button')
    model = models.FormButtonPlugin

    def get_form_fields(self, instance):
        return {}


plugin_pool.register_plugin(BooleanField)
plugin_pool.register_plugin(EmailField)
plugin_pool.register_plugin(Fieldset)
plugin_pool.register_plugin(FormPlugin)
plugin_pool.register_plugin(MultipleSelectField)
plugin_pool.register_plugin(RadioSelectField)
plugin_pool.register_plugin(SelectField)
plugin_pool.register_plugin(SubmitButton)
plugin_pool.register_plugin(TextAreaField)
plugin_pool.register_plugin(TextField)
