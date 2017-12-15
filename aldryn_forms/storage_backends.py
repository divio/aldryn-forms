import abc

import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _


DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS = {
    'default': 'aldryn_forms.storage_backends.DefaultStorageBackend',
    'no_storage': 'aldryn_forms.storage_backends.NoStorageBackend',
}
DEFAULT_ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND = 'default'
ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE = 15


def get_storage_backends():
    if hasattr(settings, 'ALDRYN_FORMS_STORAGE_BACKENDS'):
        backends = settings.ALDRYN_FORMS_STORAGE_BACKENDS
    else:
        backends = DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS

    backends = {k: import_string(v) for k, v in backends.items()}

    if any(filter(lambda x: len(x) > ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE, backends.keys())):
        raise ImproperlyConfigured(_(
            'Invalid settings.ALDRYN_FORMS_STORAGE_BACKENDS. Ensure all keys are no longer than {qty} characters.'
        ).format(qty=ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE))

    if any(filter(lambda x: not(issubclass(x, BaseStorageBackend)), backends.values())):
        raise ImproperlyConfigured(_(
            'Invalid settings.ALDRYN_FORMS_STORAGE_BACKENDS. '
            'All classes must derive from aldryn_forms.storage_backends.BaseStorageBackend'
        ))

    return backends


def storage_backend_choices(*args, **kwargs):
    choices = tuple([(key, klass.verbose_name) for key, klass in get_storage_backends().items()])
    return sorted(choices, key=lambda x: x[1])


def storage_backend_default(*args, **kwargs):
    default_backend = getattr(
        settings, 'ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND', DEFAULT_ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND
    )

    if default_backend not in get_storage_backends():
        raise ImproperlyConfigured(_(
            'Invalid settings.ALDRYN_FORMS_STORAGE_BACKENDS. Key "{key}" is not present in this config. '
            'Change your settings.ALDRYN_FORMS_STORAGE_BACKENDS to include key "{key}" '
            'or configure settings.ALDRYN_FORMS_DEFAULT_STORAGE_BACKEND accordingly.'
        ).format(key=default_backend))

    return default_backend


class BaseStorageBackend(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractproperty
    def verbose_name(self):
        pass

    @abc.abstractmethod
    def form_valid(self, cmsplugin, instance, request, form):
        raise NotImplementedError()


class DefaultStorageBackend(BaseStorageBackend):
    verbose_name = _('Regular Database Storage')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form)
        form.instance.set_recipients(recipients)
        form.save()
        cmsplugin.send_success_message(instance, request)


class NoStorageBackend(BaseStorageBackend):
    verbose_name = _('No Database Storage')

    def form_valid(self, cmsplugin, instance, request, form):
        pass
