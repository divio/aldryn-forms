# -*- coding: utf-8 -*-
from string import Template


def get_template_name(base, name, format='txt'):
    filename = '{0}.{1}'.format(name, format)

    if not base.endswith('/'):
        base += '/'
    return '{0}{1}'.format(base, filename)


def get_email_template_name(format='txt'):
    template_name = get_template_name(
        base='aldryn_forms/email_notifications/emails/',
        name='body',
        format=format,
    )
    return template_name


def get_theme_template_name(theme, format='txt'):
    template_name = get_template_name(
        base='aldryn_forms/email_notifications/emails/themes',
        name=theme,
        format=format,
    )
    return template_name


def render_text(message, context):
    template = Template(template=message)
    return template.safe_substitute(**context)
