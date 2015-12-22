# -*- coding: utf-8 -*-
try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict

try:
    from formtools.wizard.views import SessionWizardView
except ImportError:
    from django.contrib.formtools.wizard.views import SessionWizardView
