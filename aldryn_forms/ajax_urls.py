from django.urls import path

from .views import AjaxSubmit

urlpatterns = [
    path('', AjaxSubmit.as_view(), name='aldryn_forms_ajax_submit_form'),
]
