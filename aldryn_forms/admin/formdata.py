# -*- coding: utf-8 -*-
from django.contrib import admin

from .base import BaseFormSubmissionAdmin
from .forms import FormDataExportForm
from ..models import FormData


class FormDataAdmin(BaseFormSubmissionAdmin):
    change_list_template = 'admin/aldryn_forms/formsubmission/change_list.html'
    export_form = FormDataExportForm
    readonly_fields = [
        'name',
        'data',
        'language',
        'sent_at',
        'get_recipients_for_display'
    ]

    def get_recipients(self, obj):
        return obj.get_recipients()


admin.site.register(FormData, FormDataAdmin)
