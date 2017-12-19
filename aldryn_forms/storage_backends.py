# -*- coding: utf-8 -*-
import logging

from django.utils.translation import ugettext_lazy as _

from .storage_backends_base import BaseStorageBackend

logger = logging.getLogger(__name__)


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
