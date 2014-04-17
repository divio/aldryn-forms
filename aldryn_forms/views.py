# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import FormView
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from emailit.api import send_mail

from .models import FormPlugin, FormData
from .utils import (
    get_plugin_tree,
    add_form_error,
    get_form_render_data
)


class SendView(FormView):

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
        form_data = get_form_render_data(form)
        self.send_notification_emails(form_data)
        self.save_to_db(form_data)
        context = self.get_context_data(form=form, form_success_url=self.get_success_url())
        messages.success(self.request, _('The form has been sent.'))
        return self.render_to_response(context=context)

    def form_invalid(self, form):
        if self.object.error_message:
            add_form_error(form, self.object.error_message)
        return super(SendView, self).form_invalid(form)

    def get_success_url(self):
        plugin_instance = self.object.get_plugin_instance()[1]
        return plugin_instance.get_success_url(instance=self.object)

    def get_context_data(self, **kwargs):
        context = super(SendView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def send_notification_emails(self, form_data):
        recipients = self.object.get_notification_emails()
        context = {'form_name': self.object.name, 'form_data': form_data}
        send_mail(recipients=recipients,
                  context=context,
                  template_base='aldryn_forms/emails/notification')

    def save_to_db(self, form_data):
        rendered_form_data = render_to_string('aldryn_forms/snippets/_form_data.txt',
                                              {'form_data': form_data})
        form_data = FormData.objects.create(name=self.object.name,
                                            data=rendered_form_data)
        for recipient in self.object.recipients.all():
            form_data.people_notified.add(recipient)
