# -*- coding: utf-8 -*-
import warnings

__version__ = '1.0.1'

warnings.warn(
    'The "aldryn_forms.FormData" model has been deprecated in '
    'favor of aldryn_forms.FormSubmission',
    DeprecationWarning
)
