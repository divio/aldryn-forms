from email.utils import formataddr

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


str_dunder_method = '__str__'


class BaseFormSubmissionAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_at'
    list_display = [str_dunder_method, 'sent_at', 'language']
    list_filter = ['name', 'language']
    readonly_fields = [
        'name',
        'get_data_for_display',
        'language',
        'sent_at',
        'get_recipients_for_display',
    ]

    def has_add_permission(self, request):
        return False

    def get_data_for_display(self, obj):
        data = obj.get_form_data()
        html = render_to_string(
            'admin/aldryn_forms/display/submission_data.html',
            {'data': data}
        )
        return html
    get_data_for_display.allow_tags = True
    get_data_for_display.short_description = _('data')

    def get_recipients(self, obj):
        recipients = obj.get_recipients()
        formatted = [formataddr((recipient.name, recipient.email))
                     for recipient in recipients]
        return formatted

    def get_recipients_for_display(self, obj):
        people_list = self.get_recipients(obj)
        html = render_to_string(
            'admin/aldryn_forms/display/recipients.html',
            {'people': people_list},
        )
        return html
    get_recipients_for_display.allow_tags = True
    get_recipients_for_display.short_description = _('people notified')

    def get_urls(self):
        from django.conf.urls import url

        def pattern(regex, fn, name):
            args = [regex, self.admin_site.admin_view(fn)]
            return url(*args, name=self.get_admin_url(name))

        url_patterns = [
            pattern(r'export/$', self.get_form_export_view(), 'export'),
        ]

        return url_patterns + super(BaseFormSubmissionAdmin, self).get_urls()

    def get_admin_url(self, name):
        try:
            model_name = self.model._meta.model_name
        except AttributeError:
            # django <= 1.5 compat
            model_name = self.model._meta.module_name

        url_name = "%s_%s_%s" % (self.model._meta.app_label, model_name, name)
        return url_name

    def get_admin_context(self, form=None, title=None):
        opts = self.model._meta

        context = {
            'media': self.media,
            'has_change_permission': True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'current_app': self.admin_site.name,
            'app_label': opts.app_label,
        }

        if form:
            context['adminform'] = form
            context['media'] += form.media

        if title:
            context['original'] = title
        return context

    def get_form_export_view(self):
        raise NotImplementedError
