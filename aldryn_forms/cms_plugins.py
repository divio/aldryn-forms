from typing import Dict

from PIL import Image
from aldryn_forms.models import FormPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django import forms
from django.contrib.admin import TabularInline
from django.core.validators import MinLengthValidator
from django.db.models import query
from django.template.loader import select_template
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from emailit.api import send_mail
from filer.models import filemodels
from filer.models import imagemodels

from . import models
from .forms import BooleanFieldForm
from .forms import CaptchaFieldForm
from .forms import EmailFieldForm
from .forms import FileFieldForm
from .forms import FormPluginForm
from .forms import FormSubmissionBaseForm
from .forms import HiddenFieldForm
from .forms import ImageFieldForm
from .forms import MultipleSelectFieldForm
from .forms import RadioFieldForm
from .forms import RestrictedFileField
from .forms import RestrictedImageField
from .forms import SelectFieldForm
from .forms import TextAreaFieldForm
from .forms import TextFieldForm
from .helpers import get_user_name
from .models import FileUploadFieldPlugin
from .models import SerializedFormField
from .signals import form_post_save
from .signals import form_pre_save
from .sizefield.utils import filesizeformat
from .utils import get_action_backends
from .validators import MaxChoicesValidator
from .validators import MinChoicesValidator
from .validators import is_valid_recipient


class FormElement(CMSPluginBase):
    # Don't cache anything.
    cache = False
    module = _('Forms')


class FieldContainer(FormElement):
    allow_children = True


class FormPlugin(FieldContainer):
    render_template = True
    name = _('Form')
    module = _('Form types')
    model = models.FormPlugin
    form = FormPluginForm
    filter_horizontal = ['recipients']

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'redirect_type',
                'redirect_page',
                'url',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'form_template',
                'error_message',
                'success_message',
                'recipients',
                'action_backend',
                'custom_classes',
                'form_attributes',
            )
        }),
    )

    def render(self, context, instance, placeholder):
        context = super(FormPlugin, self).render(context, instance, placeholder)
        request = context['request']

        form = self.process_form(instance, request)

        if request.POST.get('form_plugin_id') == str(instance.id) and form.is_valid():
            context['post_success'] = True
            context['form_success_url'] = self.get_success_url(instance)
        context['form'] = form
        return context

    def get_render_template(self, context, instance, placeholder):
        return instance.form_template

    def form_valid(self, instance, request, form):
        action_backend = get_action_backends()[form.form_plugin.action_backend]()
        return action_backend.form_valid(self, instance, request, form)

    def form_invalid(self, instance, request, form):
        if instance.error_message:
            form._add_error(message=instance.error_message)

    def process_form(self, instance, request):
        form_class = self.get_form_class(instance)
        form_kwargs = self.get_form_kwargs(instance, request)
        form = form_class(**form_kwargs)

        if request.POST.get('form_plugin_id') == str(instance.id) and form.is_valid():
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
        elif request.POST.get('form_plugin_id') == str(instance.id) and request.method == 'POST':
            # only call form_invalid if request is POST and form is not valid
            self.form_invalid(instance, request, form)
        return form

    def get_form_class(self, instance):
        """
        Constructs form class basing on children plugin instances.
        """
        fields = self.get_form_fields(instance)
        formClass = (
            type(FormSubmissionBaseForm)
            ('AldrynDynamicForm', (FormSubmissionBaseForm,), fields)
        )
        return formClass

    def get_form_fields(self, instance: models.FormPlugin) -> Dict:
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

        if request.POST.get('form_plugin_id') == str(instance.id) and request.method in ('POST', 'PUT'):
            kwargs['data'] = request.POST.copy()
            kwargs['data']['language'] = instance.language
            kwargs['data']['form_plugin_id'] = instance.pk
            kwargs['files'] = request.FILES
        return kwargs

    def get_success_url(self, instance):
        return instance.success_url

    def send_notifications(self, instance, form):
        users = instance.recipients.exclude(email='')

        recipients = [user for user in users.iterator()
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
            (get_user_name(user), user.email) for user in recipients]
        return users_notified


class Fieldset(FieldContainer):
    render_template = True
    name = _('Fieldset')
    model = models.FieldsetPlugin

    fieldsets = (
        (None, {
            'fields': (
                'legend',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': (
                'custom_classes',
            )
        }),
    )

    def get_render_template(self, context, instance, placeholder):
        try:
            form_plugin = context['form'].form_plugin
        except KeyError:
            # technically a fieldset is not allowed outside a form.
            # unfortunately, there's no builtin way to enforce this on the cms
            form_plugin = None
        templates = self.get_template_names(instance, form_plugin)
        return select_template(templates)

    def get_template_names(self, instance, form_plugin=None):
        template_names = ['aldryn_forms/fieldset.html']

        if form_plugin:
            template = 'aldryn_forms/{}/fieldset.html'.format(form_plugin.plugin_type.lower())
            template_names.insert(0, template)
        return template_names


class Field(FormElement):
    module = _('Form fields')
    # template name is calculated based on field
    render_template = True
    model = models.FieldPlugin

    # Custom field related attributes
    form_field = None
    form_field_widget = None
    form_field_enabled_options = [
        'label',
        'name',
        'help_text',
        'required',
        'attributes',
    ]
    form_field_disabled_options = []

    # Used to configure default fieldset in admin form
    fieldset_general_fields = [
        'label',
        'name',
        'placeholder_text',
        'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        ('min_value', 'max_value',),
        'required_message',
        'custom_classes',
    ]

    def serialize_value(self, instance, value, is_confirmation=False):
        if isinstance(value, query.QuerySet):
            value = u', '.join(map(str, value))
        elif value is None:
            value = '-'
        return str(value)

    def serialize_field(self, form, field, is_confirmation=False):
        """Returns a (key, label, value) named tuple for the given field."""
        value = self.serialize_value(
            instance=field.plugin_instance,
            value=form.cleaned_data[field.name],
            is_confirmation=is_confirmation,
        )
        serialized_field = SerializedFormField(
            name=field.name,
            label=field.label,
            field_occurrence=field.field_occurrence,
            value=value,
        )
        return serialized_field

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
        if 'initial_value' in allowed_options:
            kwargs['initial'] = instance.initial_value
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
        if instance.attributes:
            attrs.update(instance.attributes)
        return attrs

    def get_form_field_widget_kwargs(self, instance):
        return {}

    def render(self, context, instance, placeholder):
        context = super(Field, self).render(context, instance, placeholder)

        form = context.get('form')

        if form and hasattr(form, 'form_plugin'):
            form_plugin = form.form_plugin
            field_name = form_plugin.get_form_field_name(field=instance)
            context['field'] = form[field_name]
        return context

    def get_render_template(self, context, instance, placeholder):
        try:
            form_plugin = context['form'].form_plugin
        except KeyError:
            # technically a field is not allowed outside a form.
            # unfortunately, there's no builtin way to enforce this on the cms
            form_plugin = None
        templates = self.get_template_names(instance, form_plugin)
        return select_template(templates)

    def get_fieldsets(self, request, obj=None):
        if self.fieldsets or self.fields:
            # Allows overriding using fieldsets or fields. If you do that none
            # of the automatic stuff kicks in and you have to take care of
            # declaring all fields you want on the form!
            # This ends up having the same behaviour as declared_fieldsets in
            # Django <1.9 had.
            return super(Field, self).get_fieldsets(request, obj=obj)

        fieldsets = [
            (None, {'fields': list(self.fieldset_general_fields)}),
        ]

        if self.fieldset_advanced_fields:
            fieldsets.append(
                (
                    _('Advanced Settings'), {
                        'classes': ('collapse',),
                        'fields': list(self.fieldset_advanced_fields),
                    }
                ))
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

    def get_template_names(self, instance, form_plugin=None):
        template_names = [
            'aldryn_forms/fields/{0}.html'.format(instance.field_type),
            'aldryn_forms/field.html',
        ]

        if form_plugin:
            template = 'aldryn_forms/{}/fields/{}.html'.format(
                form_plugin.plugin_type.lower(),
                instance.field_type,
            )
            template_names.insert(0, template)
        return template_names

    # hooks to allow processing of form data per field
    def form_pre_save(self, instance, form, **kwargs):
        pass

    def form_post_save(self, instance, form, **kwargs):
        pass


class BaseTextField(Field):
    form = TextFieldForm
    form_field = forms.CharField
    form_field_widget = forms.CharField.widget
    form_field_widget_input_type = 'text'
    form_field_enabled_options = [
        'label',
        'name',
        'help_text',
        'required',
        'max_length',
        'error_messages',
        'validators',
        'placeholder',
        'initial_value',
    ]

    def get_form_field_validators(self, instance):
        validators = []

        if instance.min_value:
            validators.append(MinLengthValidator(instance.min_value))
        return validators

    def get_form_field_widget_attrs(self, instance):
        attrs = super(BaseTextField, self).get_form_field_widget_attrs(instance)
        attrs['type'] = self.form_field_widget_input_type
        return attrs


class TextField(BaseTextField):
    name = _('Text Field')


class TextAreaField(BaseTextField):
    name = _('Text Area Field')
    model = models.TextAreaFieldPlugin
    form = TextAreaFieldForm
    form_field_widget = forms.Textarea
    fieldset_general_fields = [
        'label',
        'name',
        'placeholder_text',
        ('text_area_rows', 'text_area_columns',),
        'required',
    ]
    fieldset_advanced_fields = [
        'help_text',
        ('min_value', 'max_value',),
        'required_message',
        'custom_classes',
    ]

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


class HiddenField(BaseTextField):
    name = _('Hidden Field')
    form = HiddenFieldForm
    form_field_widget_input_type = 'hidden'
    fieldset_general_fields = ['name', 'initial_value']
    fieldset_advanced_fields = []


class PhoneField(BaseTextField):
    name = _('Phone Field')
    form_field_widget_input_type = 'phone'


class NumberField(BaseTextField):
    name = _('Number Field')
    form_field_widget_input_type = 'number'


class EmailField(BaseTextField):
    name = _('Email Field')
    model = models.EmailFieldPlugin
    form = EmailFieldForm
    form_field = forms.EmailField
    form_field_widget = forms.EmailInput
    form_field_widget_input_type = 'email'
    fieldset_advanced_fields = [
        'email_send_notification',
        'email_subject',
        'email_body',
    ] + Field.fieldset_advanced_fields
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
    fieldset_general_fields = [
        'upload_to',
    ] + Field.fieldset_general_fields
    fieldset_advanced_fields = [
        'help_text',
        'max_size',
        'required_message',
        'custom_classes',
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
            return value.absolute_uri
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
        except:  # noqa
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
    fieldset_general_fields = [
        'upload_to',
    ] + Field.fieldset_general_fields
    fieldset_advanced_fields = [
        'help_text',
        'max_size',
        ('max_width', 'max_height',),
        'required_message',
        'custom_classes',
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
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
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
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
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
        'name',
        'attributes',
        'help_text',
        'required',
        'validators',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        ('min_value', 'max_value'),
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


class MultipleCheckboxSelectField(MultipleSelectField):
    name = _('Multiple Checkbox Field')


class RadioSelectField(Field):
    name = _('Radio Select Field')

    form = RadioFieldForm
    form_field = forms.ModelChoiceField
    form_field_widget = forms.RadioSelect
    form_field_enabled_options = [
        'label',
        'name',
        'attributes',
        'help_text',
        'required',
        'error_messages',
    ]
    fieldset_general_fields = [
        'label', 'name', 'required',
    ]
    fieldset_advanced_fields = [
        'attributes',
        'help_text',
        'required_message',
        'custom_classes',
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
        fieldset_general_fields = [
            'label',
        ]
        fieldset_advanced_fields = [
            'required_message',
        ]

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
plugin_pool.register_plugin(HiddenField)
plugin_pool.register_plugin(PhoneField)
plugin_pool.register_plugin(NumberField)
plugin_pool.register_plugin(ImageField)
plugin_pool.register_plugin(Fieldset)
plugin_pool.register_plugin(MultipleSelectField)
plugin_pool.register_plugin(MultipleCheckboxSelectField)
plugin_pool.register_plugin(RadioSelectField)
plugin_pool.register_plugin(SelectField)
plugin_pool.register_plugin(SubmitButton)
plugin_pool.register_plugin(TextAreaField)
plugin_pool.register_plugin(TextField)
