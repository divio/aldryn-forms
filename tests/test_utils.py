from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.test import override_settings
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.action_backends import DefaultAction, EmailAction, NoAction
from aldryn_forms.action_backends_base import BaseAction
from aldryn_forms.utils import get_action_backends, action_backend_choices


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
