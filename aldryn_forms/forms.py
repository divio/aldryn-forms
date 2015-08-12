# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from PIL import Image

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.forms import NON_FIELD_ERRORS
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from sizefield.utils import filesizeformat

from .models import FormData, FormPlugin
from .utils import add_form_error, get_user_model


class FileSizeCheckMixin(object):
    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', None)
        super(FileSizeCheckMixin, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(FileSizeCheckMixin, self).clean(*args, **kwargs)

        if data is None:
            return

        if self.max_size is not None and data.size > self.max_size:
            raise forms.ValidationError(
                _('File size must be under %s. Current file size is %s.') % (
                    filesizeformat(self.max_size),
                    filesizeformat(data.size),
                ))
        return data


class RestrictedFileField(FileSizeCheckMixin, forms.FileField):
    pass


class RestrictedImageField(FileSizeCheckMixin, forms.ImageField):
    def __init__(self, *args, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        super(RestrictedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(RestrictedImageField, self).clean(*args, **kwargs)

        if data is None:
            return

        with Image.open(data) as img:
            width, height = img.size

        if self.max_width and width > self.max_width:
            raise forms.ValidationError(
                _('Image width must be under %s pixels. '
                  'Current width is %s pixels.') % (self.max_width, width))

        if self.max_height and height > self.max_height:
            raise forms.ValidationError(
                _('Image height must be under %s pixels. '
                  'Current height is %s pixels.') % (self.max_height, height))

        return data


def form_choices():
    form_names = FormData.objects.values_list('name', flat=True).distinct()

    for name in form_names.order_by('name'):
        yield (name, name)


class FormExportForm(forms.Form):
    excel_limit = 65536
    export_filename = 'export-{form_name}-%Y-%m-%d'

    form_name = forms.ChoiceField(choices=[])
    from_date = forms.DateField(
        label=_('from date'),
        required=False,
        widget=AdminDateWidget
    )
    to_date = forms.DateField(
        label=_('to date'),
        required=False,
        widget=AdminDateWidget
    )

    def __init__(self, *args, **kwargs):
        super(FormExportForm, self).__init__(*args, **kwargs)
        self.fields['form_name'].choices = form_choices()

    def clean(self):
        queryset = self.get_queryset()

        if queryset.count() >= self.excel_limit:
            error_message = _("Export failed! More then 65'536 entries found, exceeded Excel limitation!")
            raise forms.ValidationError(error_message)

        return self.cleaned_data

    def get_filename(self):
        data = self.cleaned_data
        form_name = data['form_name'].lower()
        filename = self.export_filename.format(form_name=slugify(form_name))
        return timezone.now().strftime(filename)

    def get_queryset(self):
        data = self.cleaned_data
        from_date, to_date = data.get('from_date'), data.get('to_date')

        queryset = FormData.objects.filter(name=data['form_name'])

        if from_date:
            lower = datetime(*from_date.timetuple()[:6]) # inclusive
            queryset = queryset.filter(sent_at__gte=lower)

        if to_date:
            upper = datetime(*to_date.timetuple()[:6]) + timedelta(days=1) # exclusive
            queryset = queryset.filter(sent_at__lt=upper)

        return queryset


class FormDataBaseForm(forms.Form):

    # these fields are internal.
    # by default we ignore all hidden fields when saving form data to db.
    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        widget=forms.HiddenInput()
    )
    form_plugin_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.form_plugin = kwargs.pop('form_plugin')
        self.request = kwargs.pop('request')
        super(FormDataBaseForm, self).__init__(*args, **kwargs)
        language = self.form_plugin.language

        self.instance = FormData(language=language, name=self.form_plugin.name)
        self.fields['language'].initial = language
        self.fields['form_plugin_id'].initial = self.form_plugin.pk

    def _add_error(self, message, field=NON_FIELD_ERRORS):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])

    def get_serialized_fields(self, is_confirmation=False):
        """
        The `is_confirmation` flag indicates if the data will be used in a
        confirmation email sent to the user submitting the form or if it will be
        used to render the data for the recipients/admin site.
        """
        for field in self.form_plugin.get_form_fields():
            plugin = field.plugin_instance.get_plugin_class_instance()
            # serialize_field can be None or SerializedFormField  namedtuple instance.
            # if None then it means we shouldn't serialize this field.
            serialized_field = plugin.serialize_field(self, field, is_confirmation)

            if serialized_field:
                yield serialized_field

    def get_serialized_field_choices(self, is_confirmation=False):
        """Renders the form data in a format suitable to be serialized.
        """
        fields = self.get_serialized_fields(is_confirmation)
        fields = [(field.label, field.value) for field in fields]
        return fields

    def get_cleaned_data(self, is_confirmation=False):
        fields = self.get_serialized_fields(is_confirmation)
        form_data = dict((field.name, field.value) for field in fields)
        return form_data

    def save(self, commit=False):
        self.instance.set_form_data(self)
        self.instance.save()


class ExtandableErrorForm(forms.ModelForm):

    def append_to_errors(self, field, message):
        add_form_error(form=self, message=message, field=field)


class FormPluginForm(ExtandableErrorForm):

    def __init__(self, *args, **kwargs):
        super(FormPluginForm, self).__init__(*args, **kwargs)

        if getattr(settings, 'ALDRYN_FORMS_SHOW_ALL_RECIPIENTS', False):
            self.fields['recipients'].queryset = get_user_model().objects.all()

    def clean(self):
        redirect_type = self.cleaned_data.get('redirect_type')
        page = self.cleaned_data.get('page')
        url = self.cleaned_data.get('url')

        if redirect_type:
            if redirect_type == FormPlugin.REDIRECT_TO_PAGE:
                if not page:
                    self.append_to_errors('page', _('Please provide CMS page for redirect.'))
                self.cleaned_data['url'] = None
            if redirect_type == FormPlugin.REDIRECT_TO_URL:
                if not url:
                    self.append_to_errors('url', _('Please provide an absolute URL for redirect.'))
                self.cleaned_data['page'] = None

        return self.cleaned_data


class BooleanFieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:  # creating new one
            initial = kwargs.pop('initial', {})
            initial['required'] = False
            kwargs['initial'] = initial
        super(BooleanFieldForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class SelectFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class RadioFieldForm(forms.ModelForm):

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message', 'custom_classes']


class CaptchaFieldForm(forms.ModelForm):

    class Meta:
        # captcha is always required
        fields = ['label', 'help_text', 'required_message']


class MinMaxValueForm(ExtandableErrorForm):

    def clean(self):
        min_value = self.cleaned_data.get('min_value')
        max_value = self.cleaned_data.get('max_value')
        if min_value and max_value and min_value > max_value:
            self.append_to_errors('min_value', _(u'Min value can not be greater then max value.'))
        return self.cleaned_data


class TextFieldForm(MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(TextFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min length')
        self.fields['min_value'].help_text = _(u'Required number of characters to type.')

        self.fields['max_value'].label = _(u'Max length')
        self.fields['max_value'].help_text = _(u'Maximum number of characters to type.')
        self.fields['max_value'].required = True

    class Meta:
        fields = ['label', 'placeholder_text', 'help_text',
                  'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class EmailFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(EmailFieldForm, self).__init__(*args, **kwargs)
        self.fields['min_value'].required = False
        self.fields['max_value'].required = False

    class Meta:
        fields = [
            'label',
            'placeholder_text',
            'help_text',
            'min_value',
            'max_value',
            'required',
            'required_message',
            'email_send_notification',
            'email_subject',
            'email_body',
            'custom_classes',
        ]


class FileFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FileFieldForm, self).__init__(*args, **kwargs)
        self.fields['help_text'].help_text = _(
            'Explanatory text displayed next to input field. Just like this '
            'one. You can use MAXSIZE as a placeholder for the maximum size '
            'configured below.')

    class Meta:
        fields = ['label', 'help_text', 'required', 'required_message',
                  'custom_classes', 'upload_to', 'max_size']


class ImageFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageFieldForm, self).__init__(*args, **kwargs)
        self.fields['help_text'].help_text = _(
            'Explanatory text displayed next to input field. Just like this '
            'one. You can use MAXSIZE, MAXWIDTH, MAXHEIGHT as a placeholders '
            'for the maximum file size and dimensions configured below.')

    class Meta:
        fields = FileFieldForm.Meta.fields + ['max_height', 'max_width']


class TextAreaFieldForm(TextFieldForm):

    def __init__(self, *args, **kwargs):
        super(TextAreaFieldForm, self).__init__(*args, **kwargs)
        self.fields['max_value'].required = False

    class Meta:
        fields = ['label', 'placeholder_text', 'help_text', 'text_area_columns',
                  'text_area_rows', 'min_value', 'max_value', 'required', 'required_message', 'custom_classes']


class MultipleSelectFieldForm(MinMaxValueForm):

    def __init__(self, *args, **kwargs):
        super(MultipleSelectFieldForm, self).__init__(*args, **kwargs)

        self.fields['min_value'].label = _(u'Min choices')
        self.fields['min_value'].help_text = _(u'Required amount of elements to chose.')

        self.fields['max_value'].label = _(u'Max choices')
        self.fields['max_value'].help_text = _(u'Maximum amount of elements to chose.')

    class Meta:
        # 'required' and 'required_message' depend on min_value field validator
        fields = ['label', 'help_text', 'min_value', 'max_value', 'custom_classes']
