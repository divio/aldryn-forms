# -*- coding: utf-8 -*-
from collections import defaultdict
from functools import partial

from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext, ugettext_lazy as _

from django_tablib.views import export

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

    def get_form_export_view(self):
        return self.form_export

    def form_export(self, request):
        form = self.export_form(request.POST or None)

        if form.is_valid():
            entries = form.get_queryset()

            if entries.exists():
                filename = form.get_filename()

                # A user can add fields to the form over time,
                # knowing this we use the latest form submission as a way
                # to get the latest form state, but this means that if a field
                # was removed then it will be ignored :(
                first_entry = entries.order_by('-sent_at')[0]

                # what follows is a bit of dark magic...
                # we call the export view in tablib with a headers dictionary, this dictionary
                # maps a key to a callable that gets passed a form submission instance and returns the value
                # for the field, we have to use a factory function in order to avoid a closure

                def clean_data(label, position):
                    def _clean_data(obj):
                        field = None
                        value = ''

                        try:
                            field = obj.get_form_data()[position]
                        except IndexError:
                            pass

                        if field and field.label == label:
                            # sanity check
                            # we need this to make sure that the field label and position remain constant
                            # otherwise we'll confuse users if a field was moved.
                            value = field.value
                        return value
                    return _clean_data

                fields = first_entry.get_form_data()

                # used to keep track of occurrences
                # in case a field with the same name appears multiple times in the form.
                occurrences = defaultdict(lambda: 1)
                headers = SortedDict()

                for position, field in enumerate(fields):
                    label = field.label

                    if label in headers:
                        occurrences[label] += 1
                        label = u'%s %s' % (label, occurrences[label])
                    headers[label] = clean_data(field.label, position)

                headers[ugettext('Language')] = 'language'
                headers[ugettext('Submitted on')] = 'sent_at'

                do_export = partial(
                    export,
                    request=request,
                    queryset=entries,
                    model=entries.model,
                    headers=headers,
                    filename=filename
                )

                try:
                    # Since django-tablib 3.1 the parameter is called file_type
                    response = do_export(file_type='xls')
                except TypeError:
                    response = do_export(format='xls')
                return response
            else:
                self.message_user(request, _("No records found"), level=messages.WARNING)
                export_url = 'admin:{}'.format(self.get_admin_url('export'))
                return redirect(export_url)

        context = RequestContext(request)
        context['errors'] = form.errors
        context.update(self.get_admin_context(form=form, title='Export'))
        return render_to_response('admin/aldryn_forms/export.html', context)


admin.site.register(FormData, FormDataAdmin)
