from django.contrib import admin

from ..models import FormSubmission
from .base import BaseFormSubmissionAdmin
from .views import FormExportWizardView


class FormSubmissionAdmin(BaseFormSubmissionAdmin):
    readonly_fields = BaseFormSubmissionAdmin.readonly_fields + ['form_url']

    def get_form_export_view(self):
        return FormExportWizardView.as_view(admin=self, file_type='xls')


admin.site.register(FormSubmission, FormSubmissionAdmin)
