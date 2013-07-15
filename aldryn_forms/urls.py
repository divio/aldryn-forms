# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from aldryn_forms.views import SendView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/$', SendView.as_view(), name='send'),
)
