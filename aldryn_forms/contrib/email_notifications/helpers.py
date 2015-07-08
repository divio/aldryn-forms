# -*- coding: utf-8 -*-
import os

from string import Template

from emailit.utils import get_template_name


EMAIL_TEMPLATES_BASE = 'aldryn_forms/email_notifications/emails/'

EMAIL_THEMES_PATH = os.path.join(EMAIL_TEMPLATES_BASE, 'themes')
EMAIL_NOTIFICATIONS_PATH = os.path.join(EMAIL_TEMPLATES_BASE, 'notification')


def get_email_template_name(name='body', suffix='txt'):
    template_name = get_template_name(
        # we don't care about language specific templates
        language=None,
        base=EMAIL_NOTIFICATIONS_PATH,
        part=name,
        suffix=suffix,
    )
    return template_name


def get_theme_template_name(theme, suffix='txt'):
    filename = '{0}.{1}'.format(theme, suffix)
    template_name = os.path.join(EMAIL_THEMES_PATH, filename)
    return template_name


def render_text(message, context):
    template = Template(template=message)
    return template.safe_substitute(**context)
