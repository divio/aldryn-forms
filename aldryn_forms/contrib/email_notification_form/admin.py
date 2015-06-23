# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from parler.admin import TranslatableAdmin
from .models import FormEmailTemplate


class FormEmailTemplateAdmin(TranslatableAdmin):
    context_variables_help_text = _('variables can be used with "$" like $variable')
    list_display = ['name']
    fields = [
        'name',
        'theme',
        'context_variables',
        'email_body_text',
        'email_body_html',
    ]
    readonly_fields = ['context_variables']

    def context_variables(self, obj):
        variables = obj.allowed_context_variables
        li_items = (u'<li>{}</li>'.format(var) for var in variables)
        unordered_list = u'<ul>{}</ul>'.format(u''.join(li_items))
        help_text = u'<p class="help">{}</p>'.format(self.context_variables_help_text)
        return unordered_list + '\n' + help_text
    context_variables.allow_tags = True
    context_variables.short_description = _('available text variables')


admin.site.register(FormEmailTemplate, FormEmailTemplateAdmin)
