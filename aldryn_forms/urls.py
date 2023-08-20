from django.urls import re_path

from .views import submit_form_view


urlpatterns = [
    re_path(r'^$', submit_form_view, name='aldryn_forms_submit_form'),
]
