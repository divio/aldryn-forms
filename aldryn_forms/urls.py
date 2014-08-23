# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns('aldryn_forms.views',
    url(r'^$', 'submit_form_view', name='aldryn_forms_submit_form'),
)
