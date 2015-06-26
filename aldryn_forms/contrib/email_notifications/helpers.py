# -*- coding: utf-8 -*-
from string import Template


def render_text(message, context):
    template = Template(template=message)
    return template.safe_substitute(**context)
