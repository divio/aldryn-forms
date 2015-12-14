# -*- coding: utf-8 -*-
import warnings

__version__ = '2.0.0'

warnings.warn(
    'The "aldryn_forms.FormData" model has been deprecated in '
    'favor of aldryn_forms.FormSubmission',
    DeprecationWarning
)
