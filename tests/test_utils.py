from django.contrib.messages.storage.base import BaseStorage
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin, create_page
from cms.operations import MOVE_PLUGIN, PASTE_PLUGIN
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.action_backends import DefaultAction, EmailAction, NoAction
from aldryn_forms.action_backends_base import BaseAction
from aldryn_forms.utils import (
    action_backend_choices, find_plugin_form, get_action_backends,
    get_form_fields_names, rename_field_name,
)


class FakeValidBackend(BaseAction):
    verbose_name = 'Fake Valid Backend'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeValidBackend2(BaseAction):
    verbose_name = 'Another Fake Valid Backend'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoInheritance():
    verbose_name = 'Fake Invalid Backend (no inheritance)'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoVerboseName(BaseAction):
    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoFormValid(BaseAction):
    verbose_name = 'Fake Invalid Backend (no form_valid() definition)'


class GetActionsTestCase(CMSTestCase):
    def test_default_backends(self):
        expected = {
            'default': DefaultAction,
            'email_only': EmailAction,
            'none': NoAction,
        }

        backends = get_action_backends()

        self.assertDictEqual(backends, expected)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x': 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = {
            'default': FakeValidBackend,
            'x': FakeValidBackend2,
        }

        backends = get_action_backends()

        self.assertDictEqual(backends, expected)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x' * 100: 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_invalid_keys_too_big(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.whatever.something.terribly.Wrong',
    })
    def test_override_invalid_path_to_class_not_found(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoInheritance',
    })
    def test_override_invalid_class_does_not_inherit_from_base_action_backend(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'custom': 'tests.test_utils.FakeValidBackend',
    })
    def test_override_invalid_key_default_missing(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoVerboseName',
    })
    def test_override_invalid_class_does_not_define_verbose_name(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoFormValid',
    })
    def test_override_invalid_class_does_not_define_form_valid(self):
        self.assertRaises(ImproperlyConfigured, get_action_backends)


class ActionChoicesTestCase(CMSTestCase):
    def test_default_backends(self):
        expected = [
            ('default', _('Default')),
            ('email_only', _('Email only')),
            ('none', _('None')),
        ]

        choices = action_backend_choices()

        self.assertEquals(choices, expected)

    @override_settings(ALDRYN_FORMS_ACTION_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x': 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = [
            ('x', 'Another Fake Valid Backend'),
            ('default', 'Fake Valid Backend'),
        ]

        choices = action_backend_choices()

        self.assertEquals(choices, expected)


class RenameFieldName(CMSTestCase):

    def setUp(self):
        page = create_page('test page', 'test_page.html', 'en')
        self.placeholder = page.placeholders.get(slot='content')

    def test_find_plugin_form_none(self):
        self.assertIsNone(find_plugin_form(None))

    def test_find_plugin_form_with_parent(self):
        parent = add_plugin(self.placeholder, 'PlaceholderPlugin', 'en')
        filed = add_plugin(parent.placeholder, 'TextField', 'en', target=parent, name="first_name")
        instance = filed.get_plugin_instance()[0]
        self.assertIsNone(find_plugin_form(instance.get_parent()))

    def test_find_plugin_form_with_parent_form(self):
        parent = add_plugin(self.placeholder, 'FormPlugin', 'en')
        filed = add_plugin(parent.placeholder, 'TextField', 'en', target=parent, name="first_name")
        instance = filed.get_plugin_instance()[0]
        self.assertEquals(find_plugin_form(instance.get_parent()).plugin_type, "FormPlugin")

    def test_find_plugin_form_with_parent_emailnotificationform(self):
        parent = add_plugin(self.placeholder, 'EmailNotificationForm', 'en')
        filed = add_plugin(parent.placeholder, 'TextField', 'en', target=parent, name="first_name")
        instance = filed.get_plugin_instance()[0]
        self.assertEquals(find_plugin_form(instance.get_parent()).plugin_type, "EmailNotificationForm")

    def _create_form_with_fields(self, name="email"):
        form = add_plugin(self.placeholder, 'FormPlugin', 'en')
        add_plugin(form.placeholder, 'TextField', 'en', target=form, name="first_name")
        add_plugin(form.placeholder, 'TextField', 'en', target=form, name="last_name")
        email = add_plugin(form.placeholder, 'EmailField', 'en', target=form, name=name)
        descendant = add_plugin(form.placeholder, 'PlaceholderPlugin', 'en', target=form)
        add_plugin(descendant.placeholder, 'TextField', 'en', target=descendant, name="is_holder")
        return (form, email)

    def test_get_form_fields_names(self):
        form, email = self._create_form_with_fields()
        names = get_form_fields_names(email.get_plugin_instance()[0], form)
        self.assertEquals(names, ['first_name', 'last_name', 'is_holder'])

    def _create_form_and_field(self, name="email"):
        form, dummy_email = self._create_form_with_fields()
        other_email = add_plugin(self.placeholder, 'EmailField', 'en', target=form, name=name)
        return (form, other_email)

    def test_rename_field_name_operation_none(self):
        form, other_email = self._create_form_and_field()
        rename_field_name(self.get_request(), None, other_email)
        self.assertEquals(other_email.name, 'email')

    def test_rename_field_name_move_plugin_with_unequal_name(self):
        form, other_email = self._create_form_and_field('email-2')
        rename_field_name(self.get_request(), MOVE_PLUGIN, other_email)
        self.assertEquals(other_email.name, 'email-2')

    def test_rename_field_name_move_plugin(self):
        form, other_email = self._create_form_and_field()
        rename_field_name(self.get_request(), MOVE_PLUGIN, other_email)
        self.assertEquals(other_email.name, 'email_')

    def test_rename_field_name_move_plugin_name_with_suffix(self):
        form, dummy_email = self._create_form_with_fields('email_')
        other_email = add_plugin(self.placeholder, 'EmailField', 'en', target=form, name='email_')
        rename_field_name(self.get_request(), MOVE_PLUGIN, other_email)
        self.assertEquals(other_email.name, 'email__')

    def test_rename_field_name_paste_plugin(self):
        form, other_email = self._create_form_and_field()
        rename_field_name(self.get_request(), PASTE_PLUGIN, other_email)
        self.assertEquals(other_email.name, 'email_')

    def test_rename_field_name_message(self):
        form, other_email = self._create_form_and_field()
        request = self.get_request()
        request._messages = BaseStorage(request)
        rename_field_name(request, MOVE_PLUGIN, other_email)
        self.assertEquals(other_email.name, 'email_')
        messages = [msg.message for msg in request._messages._queued_messages]
        self.assertEquals(messages, [
            "The field 'email' has been renamed to 'email_', because such a name is already in the form."
        ])
