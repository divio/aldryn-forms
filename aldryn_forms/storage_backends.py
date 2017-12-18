# -*- coding: utf-8 -*-
import abc
import logging

import six

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _


DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS = {
    'default': 'aldryn_forms.storage_backends.DefaultStorageBackend',
    'no_storage': 'aldryn_forms.storage_backends.NoStorageBackend',
}
ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE = 15

logger = logging.getLogger(__name__)


def get_storage_backends():
    base_error_msg = 'Invalid settings.ALDRYN_FORMS_STORAGE_BACKENDS.'
    max_key_size = ALDRYN_FORMS_STORAGE_BACKEND_KEY_MAX_SIZE

    try:
        backends = settings.ALDRYN_FORMS_STORAGE_BACKENDS
    except AttributeError:
        backends = DEFAULT_ALDRYN_FORMS_STORAGE_BACKENDS

    try:
        backends = {k: import_string(v) for k, v in backends.items()}
    except ImportError as e:
        raise ImproperlyConfigured('{} {}'.format(base_error_msg, e))

    if any(len(key) > max_key_size for key in backends):
        raise ImproperlyConfigured(
            '{} Ensure all keys are no longer than {} characters.'.format(base_error_msg, max_key_size)
        )

    if not all(issubclass(klass, BaseStorageBackend) for klass in backends.values()):
        raise ImproperlyConfigured(
            '{} All classes must derive from aldryn_forms.storage_backends.BaseStorageBackend'.format(base_error_msg)
        )

    if 'default' not in backends.keys():
        raise ImproperlyConfigured('{} Key "default" is missing.'.format(base_error_msg))

    try:
        [x() for x in backends.values()]  # check abstract base classes sanity
    except TypeError as e:
        raise ImproperlyConfigured('{} {}'.format(base_error_msg, e))
    return backends


def storage_backend_choices(*args, **kwargs):
    choices = tuple((key, klass.verbose_name) for key, klass in get_storage_backends().items())
    return sorted(choices, key=lambda x: x[1])


class BaseStorageBackend(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractproperty
    def verbose_name(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def form_valid(self, cmsplugin, instance, request, form):
        pass  # pragma: no cover


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
        form_id = form.form_plugin.id
        logger.info('Not persisting data for form {} since the storage_backend is set to "no_storage'.format(form_id))
