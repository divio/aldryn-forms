# -*- coding: utf-8 -*-
from django import template
from django.utils.text import mark_safe
from django.utils import encoding


register = template.Library()


@register.simple_tag()
def render_form_widget(field, **kwargs):
    markup =  field.as_widget(attrs=kwargs)
    return mark_safe(markup)


@register.filter()
def force_text(val):
    return encoding.force_text(val)


@register.filter()
def force_text_list(val):
    return [encoding.force_text(v) for v in val]
