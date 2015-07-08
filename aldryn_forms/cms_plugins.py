# -*- coding: utf-8 -*-
from email.utils import formataddr

from PIL import Image

from django import forms
from django.db.models import query
from django.contrib import messages
from django.contrib.admin import TabularInline
from django.core.validators import MinLengthValidator
from django.template.loader import select_template
from django.utils.translation import ugettext, ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from emailit.api import send_mail

from filer.models import filemodels, imagemodels
from sizefield.utils import filesizeformat

from . import models
from .forms import (
    RestrictedFileField,
    RestrictedImageField,
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
    FileFieldForm,
    ImageFieldForm,
)
from .models import SerializedFormField
from .signals import form_pre_save, form_post_save
from .validators import (
    is_valid_recipient,
    MinChoicesValidator,
    MaxChoicesValidator
)


class FormElement(CMSPluginBase):
    # Don't cache anything.
    cache = False
    module = _('Forms')


class FieldContainer(FormElement):
    allow_children = True


class FormPlugin(FieldContainer):
    render_template = True
    name = _('Form')
    model = models.FormPlugin
    form = FormPluginForm
    filter_horizontal = ['recipients']

    fieldsets = [
        (
            'General options',
            {'fields': ['name', 'form_template', 'error_message', 'success_message', 'recipients', 'custom_classes']}
        ),
        (
            'Redirect',
            {'fields': ['redirect_type', 'page', 'url']}
        )
    ]

    def render(self, context, instance, placeholder):
        # remove once cms 3.0.6 is released
        self.render_template = self.get_render_template(context, instance, placeholder)

        context = super(FormPlugin, self).render(context, instance, placeholder)
        request = context['request']

        form = self.process_form(instance, request)

        if form.is_valid():
            context['form_success_url'] = self.get_success_url(instance)
        context['form'] = form
        return context

    def get_render_template(self, context, instance, placeholder):
        return instance.form_template

    def form_valid(self, instance, request, form):
        recipients = self.send_notifications(instance, form)

        form.instance.set_users_notified(recipients)
        form.save()

        message = instance.success_message or ugettext('The form has been sent.')
        messages.success(request, message)

    def form_invalid(self, instance, request, form):
        if instance.error_message:
            form._add_error(message=instance.error_message)

    def process_form(self, instance, request):
        form_class = self.get_form_class(instance)
        form_kwargs = self.get_form_kwargs(instance, request)
        form = form_class(**form_kwargs)

        if form.is_valid():
            fields = [field for field in form.base_fields.values()
                      if hasattr(field, '_plugin_instance')]

            # pre save field hooks
            for field in fields:
                field._plugin_instance.form_pre_save(
                    instance=field._model_instance,
                    form=form,
                    request=request,
                )

            form_pre_save.send(
                sender=models.FormPlugin,
                instance=instance,
                form=form,
                request=request,
            )

            self.form_valid(instance, request, form)

            # post save field hooks
            for field in fields:
                field._plugin_instance.form_post_save(
                    instance=field._model_instance,
                    form=form,
                    request=request,
                )

            form_post_save.send(
                sender=models.FormPlugin,
                instance=instance,
                form=form,
                request=request,
            )
        elif request.method == 'POST':
            # only call form_invalid if request is POST and form is not valid
            self.form_invalid(instance, request, form)
        return form

    def get_form_class(self, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = self.get_form_fields(instance)
        return type(FormDataBaseForm)('AldrynDynamicForm', (FormDataBaseForm,), fields)

    def get_form_fields(self, instance):
        form_fields = {}
        fields = instance.get_form_fields()

        for field in fields:
            plugin_instance = field.plugin_instance
            field_plugin = plugin_instance.get_plugin_class_instance()
            form_fields[field.name] = field_plugin.get_form_field(plugin_instance)
        return form_fields

    def get_form_kwargs(self, instance, request):
        kwargs = {
            'form_plugin': instance,
            'request': request,
        }

        if request.method in ('POST', 'PUT'):
            kwargs['data'] = request.POST.copy()
            kwargs['data']['language'] = instance.language
            kwargs['data']['form_plugin_id'] = instance.pk
            kwargs['files'] = request.FILES
        return kwargs

    def get_success_url(self, instance):
        if instance.redirect_type == models.FormPlugin.REDIRECT_TO_PAGE:
            return instance.page.get_absolute_url()
        elif instance.redirect_type == models.FormPlugin.REDIRECT_TO_URL:
            return instance.url
        else:
            raise RuntimeError('Form is not configured properly.')

    def send_notifications(self, instance, form):
        users = instance.recipients.only('first_name', 'last_name', 'email')

        recipients = [user for user in users.exclude(email='')
                      if is_valid_recipient(user.email)]

        context = {
            'form_name': instance.name,
            'form_data': form.get_serialized_field_choices(),
            'form_plugin': instance,
        }

        send_mail(
            recipients=[user.email for user in recipients],
            context=context,
            template_base='aldryn_forms/emails/notification',
            language=instance.language,
        )

        users_notified = [
            formataddr((user.get_full_name(), user.email)) for user in recipients]
        return users_notified


class Fieldset(FieldContainer):
    render_template = 'aldryn_forms/fieldset.html'
    name = _('Fieldset')
    model = models.FieldsetPlugin


class Field(FormElement):
    module = _('Form fields')
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

    def serialize_value(self, instance, value, is_confirmation=False):
        if isinstance(value, query.QuerySet):
            value = u', '.join(map(unicode, value))
        elif value is None:
            value = '-'
        return unicode(value)

    def serialize_field(self, form, field, is_confirmation=False):
        """Returns a (key, label, value) named tuple for the given field."""
        value = self.serialize_value(
            instance=field.plugin_instance,
            value=form.cleaned_data[field.name],
            is_confirmation=is_confirmation
        )
        return SerializedFormField(name=field.name, label=field.label, value=value)

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

        if form and hasattr(form, 'form_plugin'):
            form_plugin = form.form_plugin
            field_name = form_plugin.get_form_field_name(field=instance)
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
    def form_pre_save(self, instance, form, **kwargs):
        pass

    def form_post_save(self, instance, form, **kwargs):
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
    fieldset_general_fields = Field.fieldset_general_fields + [
        'email_send_notification',
        'email_subject',
        'email_body',
    ]
    email_template_base = 'aldryn_forms/emails/user/notification'

    def send_notification_email(self, email, form, form_field_instance):
        context = {
            'form_name': form.instance.name,
            'form_data': form.get_serialized_field_choices(is_confirmation=True),
            'body_text': form_field_instance.email_body,
        }
        send_mail(
            recipients=[email],
            context=context,
            subject=form_field_instance.email_subject,
            template_base=self.email_template_base
        )

    def form_post_save(self, instance, form, **kwargs):
        field_name = form.form_plugin.get_form_field_name(field=instance)

        email = form.cleaned_data.get(field_name)

        if email and instance.email_send_notification:
            self.send_notification_email(email, form, instance)


class FileField(Field):
    name = _('File upload field')

    model = models.FileUploadFieldPlugin

    form = FileFieldForm
    form_field = RestrictedFileField
    form_field_widget = RestrictedFileField.widget
    form_field_enabled_options = [
        'label',
        'help_text',
        'required',
        'error_messages',
        'validators',
    ]
    fieldset_general_fields = Field.fieldset_general_fields + [
        'upload_to',
        'max_size',
    ]

    def get_form_field_kwargs(self, instance):
        kwargs = super(FileField, self).get_form_field_kwargs(instance)
        if instance.max_size:
            if 'help_text' in kwargs:
                kwargs['help_text'] = kwargs['help_text'].replace(
                    'MAXSIZE', filesizeformat(instance.max_size))
            kwargs['max_size'] = instance.max_size
        return kwargs

    def serialize_value(self, instance, value, is_confirmation=False):
        if value:
            return (value.original_filename if is_confirmation
                    else value.absolute_uri)
        else:
            return '-'

    def form_pre_save(self, instance, form, **kwargs):
        """Save the uploaded file to django-filer

        The type of model (file or image) is automatically chosen by trying to
        open the uploaded file.
        """
        request = kwargs['request']

        field_name = form.form_plugin.get_form_field_name(field=instance)

        uploaded_file = form.cleaned_data[field_name]

        if uploaded_file is None:
            return

        try:
            with Image.open(uploaded_file) as img:
                img.verify()
        except:
            model = filemodels.File
        else:
            model = imagemodels.Image

        filer_file = model(
            folder=instance.upload_to,
            file=uploaded_file,
            name=uploaded_file.name,
            original_filename=uploaded_file.name,
            is_public=True,
        )
        filer_file.save()

        # NOTE: This is a hack to make the full URL available later when we
        # need to serialize this field. We avoid to serialize it here directly
        # as we could still need access to the original filer File instance.
        filer_file.absolute_uri = request.build_absolute_uri(filer_file.url)

        form.cleaned_data[field_name] = filer_file


class ImageField(FileField):
    name = _('Image upload field')

    model = models.ImageUploadFieldPlugin

    form = ImageFieldForm
    form_field = RestrictedImageField
    form_field_widget = RestrictedImageField.widget
    fieldset_general_fields = Field.fieldset_general_fields + [
        'upload_to',
        'max_size',
        'max_width',
        'max_height',
    ]

    def get_form_field_kwargs(self, instance):
        kwargs = super(ImageField, self).get_form_field_kwargs(instance)

        if instance.max_width:
            if 'help_text' in kwargs:
                kwargs['help_text'] = kwargs['help_text'].replace(
                    'MAXWIDTH', str(instance.max_width))
            kwargs['max_width'] = instance.max_width

        if instance.max_height:
            if 'help_text' in kwargs:
                kwargs['help_text'] = kwargs['help_text'].replace(
                    'MAXHEIGHT', str(instance.max_height))
            kwargs['max_height'] = instance.max_height

        return kwargs


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

    def serialize_value(self, instance, value, is_confirmation=False):
        return ugettext('Yes') if value else ugettext('No')


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
        for opt in kwargs['queryset']:
            if opt.default_value:
                kwargs['initial'] = opt.pk
                break
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

        kwargs['initial'] = [o.pk for o in kwargs['queryset'] if o.default_value]
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
        for opt in kwargs['queryset']:
            if opt.default_value:
                kwargs['initial'] = opt.pk
                break
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

        def serialize_field(self, *args, **kwargs):
            # None means don't serialize me
            return None

    plugin_pool.register_plugin(CaptchaField)


class SubmitButton(FormElement):
    render_template = 'aldryn_forms/submit_button.html'
    name = _('Submit Button')
    model = models.FormButtonPlugin


plugin_pool.register_plugin(BooleanField)
plugin_pool.register_plugin(EmailField)
plugin_pool.register_plugin(FileField)
plugin_pool.register_plugin(ImageField)
plugin_pool.register_plugin(Fieldset)
plugin_pool.register_plugin(FormPlugin)
plugin_pool.register_plugin(MultipleSelectField)
plugin_pool.register_plugin(RadioSelectField)
plugin_pool.register_plugin(SelectField)
plugin_pool.register_plugin(SubmitButton)
plugin_pool.register_plugin(TextAreaField)
plugin_pool.register_plugin(TextField)
