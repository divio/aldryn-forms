try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict  # noqa

try:
    from formtools.wizard.views import SessionWizardView
except ImportError:
    from django.contrib.formtools.wizard.views import SessionWizardView  # noqa

try:
    from cms.utils.plugins import build_plugin_tree
except ImportError:
    from cms.utils.plugins import get_plugins_as_layered_tree as build_plugin_tree  # noqa
