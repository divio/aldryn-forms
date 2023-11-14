from django.dispatch import Signal


# Provides arguments: instance, form, request
form_pre_save = Signal()
form_post_save = Signal()
