import pydoc

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS = {
    'default': 'aldryn_forms.storage_backends.DefaultStorageBackend',
    'no_storage': 'aldryn_forms.storage_backends.NoStorageBackend',
}
DEFAULT_ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND = 'default'
ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE = 15


def get_storage_backends():
    backends = DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS
    backends.update(getattr(settings, 'ALDRYN_FORMS_STORAGE_BACKENDS', {}))

    if any(filter(lambda x: len(x) > ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE, backends.keys())):
        raise ImproperlyConfigured(
            _('Invalid ALDRYN_FORMS_STORAGE_BACKENDS settings. Ensure all keys are no longer than {} characters.')
            .format(ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE)
        )

    return {k: pydoc.locate(v) for k, v in backends.items()}


def storage_backend_choices(*args, **kwargs):
    choices = tuple([(key, klass.verbose_name) for key, klass in get_storage_backends().items()])
    return sorted(choices, key=lambda x: x[1])


def storage_backend_default(*args, **kwargs):
    default_backend = getattr(settings, 'ALDRYN_FORMS_STORAGE_BACKENDS', DEFAULT_ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND)

    if default_backend not in get_storage_backends():
        raise ImproperlyConfigured(
            _('Invalid ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND settings. Key "{}" is not a valid option for this config.')
            .format(default_backend)
        )

    return default_backend


class DefaultStorageBackend(object):
    verbose_name = 'Regular Database Storage'

    def form_valid(self, instance, request, form):
        recipients = self.send_notifications(instance, form)
        form.instance.set_recipients(recipients)
        form.save()
        self.send_success_message(instance, request)


class NoStorageBackend(object):
    verbose_name = 'No Database Storage'

    def form_valid(self, instance, request, form):
        pass
