from django.utils.translation import ugettext_lazy as _
from django.test import override_settings
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.utils import storage_backend_choices


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
