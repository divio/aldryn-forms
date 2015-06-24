# -*- coding: utf-8 -*-
from string import Template


def render_message(self, message, context):
    template = Template(template=message)
    return template.safe_substitute(**context)
