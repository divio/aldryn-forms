from django import forms as django_forms
from django.forms.models import modelform_factory

from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms import forms, models


class UniqueFieldNameMixinTest(CMSTestCase):

    def setUp(self):
        page = create_page('test page', 'test_page.html', 'en')
        self.placeholder = page.placeholders.get(slot='content')
        self.form = add_plugin(self.placeholder, 'FormPlugin', 'en')
        add_plugin(self.form.placeholder, 'TextField', 'en', target=self.form, name="first_name")
        add_plugin(self.form.placeholder, 'TextField', 'en', target=self.form, name="last_name")
        descendant = add_plugin(self.form.placeholder, 'PlaceholderPlugin', 'en', target=self.form)
        self.email = add_plugin(self.form.placeholder, 'EmailField', 'en', target=descendant, name="email")

    def test_clean_name(self):
        mixin = forms.UniqueFieldNameMixin()
        mixin.instance = self.email
        mixin.cleaned_data = {'name': 'email'}
        mixin.clean_name()
        self.assertEquals(mixin.instance.name, "email")

    def _test_not_unique_field_name(self, field):
        field.instance = add_plugin(self.placeholder, 'EmailField', 'en', target=self.form, name="email")
        field.cleaned_data = {'name': 'email'}
        message = 'This field name is already used in the form. Please select another.'
        with self.assertRaisesMessage(django_forms.ValidationError, message):
            field.clean_name()

    def test_unique_field_mixin(self):
        self._test_not_unique_field_name(forms.UniqueFieldNameMixin())

    def test_restricted_file_field(self):
        self._test_not_unique_field_name(forms.RestrictedFileField())

    def test_restricted_image_field(self):
        self._test_not_unique_field_name(forms.RestrictedImageField())

    def test_boolean_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.BooleanFieldForm)
        self._test_not_unique_field_name(Field())

    def test_select_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.SelectFieldForm)
        self._test_not_unique_field_name(Field())

    def test_radio_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.RadioFieldForm)
        self._test_not_unique_field_name(Field())

    def test_captcha_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.CaptchaFieldForm)
        self._test_not_unique_field_name(Field())

    def test_min_max_value_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.MinMaxValueForm, exclude=[])
        self._test_not_unique_field_name(Field())

    def test_text_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.TextFieldForm)
        self._test_not_unique_field_name(Field())

    def test_hidden_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.HiddenFieldForm)
        self._test_not_unique_field_name(Field())

    def test_email_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.EmailFieldForm, exclude=(
            'email_send_notification', 'email_body', 'email_subject'))
        self._test_not_unique_field_name(Field())

    def test_file_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.FileFieldForm, exclude=('upload_to', 'max_size'))
        self._test_not_unique_field_name(Field())

    def test_image_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.ImageFieldForm, exclude=(
            'max_width', 'max_size', 'upload_to', 'max_height'))
        self._test_not_unique_field_name(Field())

    def test_text_area_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.TextAreaFieldForm, exclude=(
            'text_area_columns', 'text_area_rows'))
        self._test_not_unique_field_name(Field())

    def test_multiple_select_field_form(self):
        Field = modelform_factory(models.FieldPlugin, forms.MultipleSelectFieldForm)
        self._test_not_unique_field_name(Field())
