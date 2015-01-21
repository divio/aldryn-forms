# -*- coding: utf-8 -*-
from django.dispatch import Signal

form_pre_save = Signal(providing_args=['instance', 'form', 'request'])
form_post_save = Signal(providing_args=['instance', 'form', 'request'])
