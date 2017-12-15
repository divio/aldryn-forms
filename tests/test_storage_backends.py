from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.utils.translation import ugettext_lazy as _
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.storage_backends import (
    get_storage_backends, storage_backend_choices, storage_backend_default,
    BaseStorageBackend, DefaultStorageBackend, NoStorageBackend,
)


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
        'default': 'tests.test_storage_backends.FakeValidBackend',
        'x': 'tests.test_storage_backends.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = {
            'default': FakeValidBackend,
            'x': FakeValidBackend2,
        }

        backends = get_storage_backends()

        self.assertDictEqual(backends, expected)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_storage_backends.FakeValidBackend',
        'x' * 100: 'tests.test_storage_backends.FakeValidBackend',
    })
    def test_override_invalid_keys_too_big(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.whatever.something.terribly.Wrong',
    })
    def test_override_invalid_path_to_class_not_found(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_storage_backends.FakeInvalidBackendNoInheritance',
    })
    def test_override_invalid_class_does_not_inherit_from_base_storage_backend(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_storage_backends.FakeInvalidBackendNoVerboseName',
    })
    def test_override_invalid_class_does_not_define_verbose_name(self):
        self.assertRaises(ImproperlyConfigured, get_storage_backends)

    @override_settings(ALDRYN_FORMS_STORAGE_BACKENDS={
        'default': 'tests.test_storage_backends.FakeInvalidBackendNoFormValid',
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
        'default': 'tests.test_storage_backends.FakeValidBackend',
        'x': 'tests.test_storage_backends.FakeValidBackend2',
    })
    def test_override_valid(self):
        expected = [
            ('x', 'Another Fake Valid Backend'),
            ('default', 'Fake Valid Backend'),
        ]

        choices = storage_backend_choices()

        self.assertEquals(choices, expected)


class StorageBackendDefaultTestCase(CMSTestCase):
    def test_default(self):
        self.assertEquals(storage_backend_default(), 'default')

    @override_settings(ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND='no_storage')
    def test_override(self):
        self.assertEquals(storage_backend_default(), 'no_storage')

    @override_settings(ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND='not_found')
    def test_invalid(self):
        self.assertRaises(ImproperlyConfigured, storage_backend_default)
