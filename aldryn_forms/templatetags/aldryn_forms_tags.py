# -*- coding: utf-8 -*-
from django import template
from django.utils.text import mark_safe


register = template.Library()


@register.simple_tag()
def render_form_widget(field, **kwargs):
    markup =  field.as_widget(attrs=kwargs)
    return mark_safe(markup)
