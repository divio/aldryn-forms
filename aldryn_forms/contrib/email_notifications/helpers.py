# -*- coding: utf-8 -*-
from string import Template


def get_theme_template_name(theme, format='html'):
    return 'aldryn_forms/email_notifications/emails/themes/{0}.{1}'.format(theme, format)


def render_text(message, context):
    template = Template(template=message)
    return template.safe_substitute(**context)
