# -*- coding: utf-8 -*-
from django import template
from django.utils.text import mark_safe
from django.utils import encoding


register = template.Library()


@register.assignment_tag(takes_context=True)
def render_notification_text(context, email_notification, email_type):
    text_context = context.get('text_context')

    if not text_context or not email_notification:
        return

    render_func = 'render_%s' % email_type
    message = getattr(email_notification, render_func)(context=text_context)
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
