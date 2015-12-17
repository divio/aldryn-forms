# -*- coding: utf-8 -*-
from django import get_version
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import get_language_from_request, ugettext
from aldryn_forms.admin.exporter import Exporter

try:
    from formtools.wizard.views import SessionWizardView
except ImportError:
    from django.contrib.formtools.wizard.views import SessionWizardView

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
        opts = self.admin.model._meta
        app_label = opts.app_label
        context = super(FormExportWizardView, self).get_context_data(form, **kwargs)
        context.update({
            'adminform': form,
            'media': self.admin.media + form.media,
            'has_change_permission': True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'current_app': self.admin.admin_site.name,
            'app_label': app_label,
            'original': 'Export',
        })
        return context

    def get_form_initial(self, step):
        initial = super(FormExportWizardView, self).get_form_initial(step)

        if step == self.steps.first:
            initial['language'] = get_language_from_request(
                self.request,
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

    def done(self, form_list, **kwargs):
        """
        this step only runs if all forms are valid.
        """
        step_1_form = form_list[0]
        step_2_form = form_list[1]

        queryset = step_1_form.get_queryset()

        exporter = Exporter(queryset=queryset)
        dataset = exporter.get_dataset(fields=step_2_form.get_fields())

        filename = '%s.%s' % (step_1_form.get_filename(), self.file_type)

        content_type = mimetype_map.get(
            self.file_type,
            'application/octet-stream'
        )

        response_kwargs = {}

        if get_version().split('.')[1] > 6:
            response_kwargs['content_type'] = content_type
        else:
            # Django <= 1.6 compatibility
            response_kwargs['mimetype'] = content_type

        response = HttpResponse(dataset.xls, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
