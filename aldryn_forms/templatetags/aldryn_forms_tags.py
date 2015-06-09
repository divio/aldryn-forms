# -*- coding: utf-8 -*-
from django import template
from django.utils.text import mark_safe
from django.utils import encoding


register = template.Library()


@register.assignment_tag(takes_context=True)
def render_form_email_message(context, email_template, email_type):
    if not email_template:
        return
    render_func = 'render_%s_message' % email_type
    message = getattr(email_template, render_func)(context=context)
    return mark_safe(message)


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
