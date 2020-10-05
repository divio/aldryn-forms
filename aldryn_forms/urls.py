from django.conf.urls import url

from .views import submit_form_view


urlpatterns = [
    url(r'^$', submit_form_view, name='aldryn_forms_submit_form'),
]
