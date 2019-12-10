from django.urls import path

from .views import AjaxSubmit
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', csrf_exempt(AjaxSubmit.as_view()), name='aldryn_forms_ajax_submit_form'),
]
