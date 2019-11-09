from django.urls import path

from .views import submit_form_view


urlpatterns = [
    path('', submit_form_view, name='aldryn_forms_submit_form'),
]
