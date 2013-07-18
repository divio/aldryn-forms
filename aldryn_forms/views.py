# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _

from aldryn_forms.models import FormPlugin
from aldryn_forms.utils import get_plugin_tree, append_non_field_form_error


class SendView(FormView):

    template_name = 'aldryn_forms/send.html'

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super(SendView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super(SendView, self).post(*args, **kwargs)

    def get_object(self):
        return get_plugin_tree(FormPlugin, pk=self.kwargs['pk'])

    def get_form_class(self):
        plugin_instance = self.object.get_plugin_instance()[1]
        return plugin_instance.get_form_class(instance=self.object)

    def form_valid(self, form):
        messages.success(self.request, _('The form has been sent.'))
        return super(SendView, self).form_valid(form)

    def form_invalid(self, form):
        if self.object.error_message:
            append_non_field_form_error(form, self.object.error_message)
        return super(SendView, self).form_invalid(form)

    def get_success_url(self):
        plugin_instance = self.object.get_plugin_instance()[1]
        return plugin_instance.get_success_url(instance=self.object)

    def get_context_data(self, **kwargs):
        context = super(SendView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context
