# -*- coding: utf-8 -*-
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import resolve
from django.views.generic import FormView
from .models import FormPlugin
from .utils import get_plugin_tree
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

try:
    from cms.utils.page import get_page_from_request, get_page_from_path
except ImportError:
    # for django-cms<3.5
    from cms.utils.page_resolver import get_page_from_request, get_page_from_path


@method_decorator(csrf_exempt, name='dispatch')
class AjaxSubmit(FormView):
    # template_name = 'aldryn_forms/form.html'

    def post(self, request, *args, **kwargs):
        cms_page = get_page_from_path(get_current_site(request), request.POST.get('page_path', '')[1:])
        if not cms_page:
            return HttpResponseBadRequest()
        context = {
            'current_app': resolve(request.path).namespace,
            'current_page': cms_page,
        }
        form_plugin_id = request.POST.get('form_plugin_id') or ''
        if not form_plugin_id.isdigit():
            # fail if plugin_id has been tampered with
            return HttpResponseBadRequest()
        try:
            # I believe this could be an issue as we don't check if the form submitted
            # is in anyway tied to this page.
            # But then we have a problem with static placeholders :(
            form_plugin = get_plugin_tree(FormPlugin, pk=form_plugin_id)
        except FormPlugin.DoesNotExist:
            return HttpResponseBadRequest()
        form_plugin_instance = form_plugin.get_plugin_instance()[1]
        # saves the form if it's valid
        form = form_plugin_instance.process_form(form_plugin, request)
        success_url = form_plugin_instance.get_success_url(instance=form_plugin)
        if form.is_valid():
            if success_url:
                return HttpResponseRedirect(success_url)
            context['post_success'] = True
        return render(request, 'aldryn_forms/form.html', context)


def submit_form_view(request):
    cms_page = get_page_from_request(request)

    if not cms_page:
        return HttpResponseBadRequest()

    template = cms_page.get_template()

    context = {
        'current_app': resolve(request.path).namespace,
        'current_page': cms_page,
    }

    if request.method == 'POST':
        form_plugin_id = request.POST.get('form_plugin_id') or ''

        if not form_plugin_id.isdigit():
            # fail if plugin_id has been tampered with
            return HttpResponseBadRequest()

        try:
            # I believe this could be an issue as we don't check if the form submitted
            # is in anyway tied to this page.
            # But then we have a problem with static placeholders :(
            form_plugin = get_plugin_tree(FormPlugin, pk=form_plugin_id)
        except FormPlugin.DoesNotExist:
            return HttpResponseBadRequest()

        form_plugin_instance = form_plugin.get_plugin_instance()[1]
        # saves the form if it's valid
        form = form_plugin_instance.process_form(form_plugin, request)
        success_url = form_plugin_instance.get_success_url(instance=form_plugin)

        if form.is_valid() and success_url:
            return HttpResponseRedirect(success_url)
    return render(request, template, context)
