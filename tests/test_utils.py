from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.test import override_settings
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.storage_backends import DefaultStorageBackend, NoStorageBackend
from aldryn_forms.storage_backends_base import BaseStorageBackend
from aldryn_forms.utils import get_storage_backends, storage_backend_choices


class FakeValidBackend(BaseStorageBackend):
    verbose_name = 'Fake Valid Backend'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeValidBackend2(BaseStorageBackend):
    verbose_name = 'Another Fake Valid Backend'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoInheritance():
    verbose_name = 'Fake Invalid Backend (no inheritance)'

    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoVerboseName(BaseStorageBackend):
    def form_valid(self, cmsplugin, instance, request, form):
        pass


class FakeInvalidBackendNoFormValid(BaseStorageBackend):
    verbose_name = 'Fake Invalid Backend (no form_valid() definition)'


class GetStorageBackendsTestCase(CMSTestCase):
    def test_default_backends(self):
        expected = {
            'default': DefaultStorageBackend,
            'no_storage': NoStorageBackend,
        }

        backends = get_storage_backends()

        self.assertDictEqual(backends, expected)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x': 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = {
            'default': FakeValidBackend,
            'x': FakeValidBackend2,
        }

        backends = get_storage_backends()

        self.assertDictEqual(backends, expected)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x' * 100: 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_invalid_keys_too_big(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.whatever.something.terribly.Wrong',
    })
    def test_override_invalid_path_to_class_not_found(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoInheritance',
    })
    def test_override_invalid_class_does_not_inherit_from_base_storage_backend(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'custom': 'tests.test_utils.FakeValidBackend',
    })
    def test_override_invalid_key_default_missing(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoVerboseName',
    })
    def test_override_invalid_class_does_not_define_verbose_name(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeInvalidBackendNoFormValid',
    })
    def test_override_invalid_class_does_not_define_form_valid(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)


class StorageBackendChoicesTestCase(CMSTestCase):
    def test_default_backends(self):
        expected = [
            ('no_storage', _('No Database Storage')),
            ('default', _('Regular Database Storage')),
        ]

        choices = storage_backend_choices()

        self.assertEquals(choices, expected)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_utils.FakeValidBackend',
        'x': 'tests.test_utils.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = [
            ('x', 'Another Fake Valid Backend'),
            ('default', 'Fake Valid Backend'),
        ]

        choices = storage_backend_choices()

        self.assertEquals(choices, expected)
