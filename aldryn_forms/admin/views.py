# -*- coding: utf-8 -*-
from django import get_version
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import get_language_from_request, ugettext

from ..compat import SessionWizardView
from .exporter import Exporter
from .forms import FormExportStep1Form, FormExportStep2Form


mimetype_map = {
    'xls': 'application/vnd.ms-excel',
    'csv': 'text/csv',
    'html': 'text/html',
    'yaml': 'text/yaml',
    'json': 'application/json',
}


class FormExportWizardView(SessionWizardView):
    admin = None
    file_type = None
    form_list = [
        FormExportStep1Form,
        FormExportStep2Form,
    ]

    template_name = 'admin/aldryn_forms/export_wizard.html'

    def get_context_data(self, form, **kwargs):
        context = super(FormExportWizardView, self).get_context_data(form, **kwargs)
        context.update(self.admin.get_admin_context(form=form, title='Export'))
        return context

    def get_form_initial(self, step):
        initial = super(FormExportWizardView, self).get_form_initial(step)

        if step == self.steps.first:
            initial['language'] = get_language_from_request(
                request=self.request,
                check_path=True
            )
        return initial

    def get_form_kwargs(self, step=None):
        """
        Returns the keyword arguments for instantiating the form
        (or formset) on the given step.
        """
        kwargs = super(FormExportWizardView, self).get_form_kwargs(step)

        if step == self.steps.last:
            form = self.get_form(
                step=self.steps.first,
                data=self.storage.get_step_data(self.steps.first),
            )
            form.full_clean()

            kwargs['submissions'] = form.get_queryset()
        return kwargs

    def render_next_step(self, form, **kwargs):
        next_step = self.steps.next

        if next_step == self.steps.last and not form.get_queryset().exists():
            self.storage.reset()
            self.admin.message_user(self.request, ugettext("No records found"), level=messages.WARNING)
            export_url = 'admin:{}'.format(self.admin.get_admin_url('export'))
            return redirect(export_url)
        return super(FormExportWizardView, self).render_next_step(form, **kwargs)

    def get_content_type(self):
        content_type = mimetype_map.get(
            self.file_type,
            'application/octet-stream'
        )
        return content_type

    def done(self, form_list, **kwargs):
        """
        this step only runs if all forms are valid.
        """
        form_iter = iter(form_list)
        step_1_form = next(form_iter)
        step_2_form = next(form_iter)

        fields = step_2_form.get_fields()
        queryset = step_1_form.get_queryset()

        dataset = Exporter(queryset=queryset).get_dataset(fields=fields)

        filename = step_1_form.get_filename(extension=self.file_type)

        content_type = self.get_content_type()

        response_kwargs = {}

        if int(get_version().split('.')[1]) > 6:
            response_kwargs['content_type'] = content_type
        else:
            # Django <= 1.6 compatibility
            response_kwargs['mimetype'] = content_type

        response = HttpResponse(dataset.xls, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
