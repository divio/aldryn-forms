# -*- coding: utf-8 -*-
from django.contrib import admin

from .base import BaseFormSubmissionAdmin
from .views import FormExportWizardView
from ..models import FormSubmission


class FormSubmissionAdmin(BaseFormSubmissionAdmin):
    readonly_fields = BaseFormSubmissionAdmin.readonly_fields + ['form_url']

    def get_form_export_view(self):
        return FormExportWizardView.as_view(admin=self, file_type='xls')


admin.site.register(FormSubmission, FormSubmissionAdmin)
