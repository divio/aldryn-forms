# -*- coding: utf-8 -*-
import logging

from django.utils.translation import ugettext_lazy as _

from .action_backends_base import BaseAction

logger = logging.getLogger(__name__)


class DefaultAction(BaseAction):
    verbose_name = _('Default action backend')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form)
        form.instance.set_recipients(recipients)
        form.save()
        cmsplugin.send_success_message(instance, request)


class EmailAction(BaseAction):
    verbose_name = _('Email action backend')

    def form_valid(self, cmsplugin, instance, request, form):
        recipients = cmsplugin.send_notifications(instance, form)
        logger.info('Sent email notifications to {} recipients.'.format(len(recipients)))


class NoAction(BaseAction):
    verbose_name = _('No action backend')

    def form_valid(self, cmsplugin, instance, request, form):
        form_id = form.form_plugin.id
        logger.info('Not persisting data for "{}" since action_backend is set to "no_action"'.format(form_id))
