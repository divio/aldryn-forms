# -*- coding: utf-8 -*-
from django.contrib import admin

from .base import BaseFormSubmissionAdmin
from .forms import FormSubmissionExportForm
from ..models import FormSubmission


class FormSubmissionAdmin(BaseFormSubmissionAdmin):
    readonly_fields = BaseFormSubmissionAdmin.readonly_fields + ['form_url']
    export_form = FormSubmissionExportForm


admin.site.register(FormSubmission, FormSubmissionAdmin)
