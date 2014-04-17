# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import FormData


class FormDataAdmin(admin.ModelAdmin):

    date_hierarchy = 'sent_at'
    list_display = ['__unicode__', 'sent_at']
    list_filter = ['name', 'people_notified']
    model = FormData
    readonly_fields = ['name', 'data', 'sent_at', 'people_notified']

admin.site.register(FormData, FormDataAdmin)
