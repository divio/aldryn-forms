# -*- coding: utf-8 -*-
from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'aldryn_forms.views.submit_form_view', name='aldryn_forms_submit_form'),
]
