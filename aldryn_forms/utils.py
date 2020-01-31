# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from cms.operations import MOVE_PLUGIN, PASTE_PLUGIN
from cms.utils.moderator import get_cmsplugin_queryset
from cms.utils.plugins import downcast_plugins

from .action_backends_base import BaseAction
from .compat import build_plugin_tree


DEFAULT_ALDRYN_FORMS_ACTION_BACKENDS = {
    'default': 'aldryn_forms.action_backends.DefaultAction',
    'email_only': 'aldryn_forms.action_backends.EmailAction',
    'none': 'aldryn_forms.action_backends.NoAction',
}
ALDRYN_FORMS_ACTION_BACKEND_KEY_MAX_SIZE = 15


def get_action_backends():
    base_error_msg = 'Invalid settings.ALDRYN_FORMS_ACTION_BACKENDS.'
    max_key_size = ALDRYN_FORMS_ACTION_BACKEND_KEY_MAX_SIZE

    try:
        backends = settings.ALDRYN_FORMS_ACTION_BACKENDS
    except AttributeError:
        backends = DEFAULT_ALDRYN_FORMS_ACTION_BACKENDS

    try:
        backends = {k: import_string(v) for k, v in backends.items()}
    except ImportError as e:
        raise ImproperlyConfigured('{} {}'.format(base_error_msg, e))

    if any(len(key) > max_key_size for key in backends):
        raise ImproperlyConfigured(
            '{} Ensure all keys are no longer than {} characters.'.format(base_error_msg, max_key_size)
        )

    if not all(issubclass(klass, BaseAction) for klass in backends.values()):
        raise ImproperlyConfigured(
            '{} All classes must derive from aldryn_forms.action_backends_base.BaseAction'
            .format(base_error_msg)
        )

    if 'default' not in backends.keys():
        raise ImproperlyConfigured('{} Key "default" is missing.'.format(base_error_msg))

    try:
        [x() for x in backends.values()]  # check abstract base classes sanity
    except TypeError as e:
        raise ImproperlyConfigured('{} {}'.format(base_error_msg, e))
    return backends


def action_backend_choices(*args, **kwargs):
    choices = tuple((key, klass.verbose_name) for key, klass in get_action_backends().items())
    return sorted(choices, key=lambda x: x[1])


def get_user_model():
    """
    Wrapper for get_user_model with compatibility for 1.5
    """
    # Notice these imports happen here to be compatible with django 1.7
    try:
        from django.contrib.auth import get_user_model as _get_user_model
    except ImportError:  # django < 1.5
        from django.contrib.auth.models import User
    else:
        User = _get_user_model()
    return User


def get_nested_plugins(parent_plugin, include_self=False):
    """
    Returns a flat list of plugins from parent_plugin
    """
    found_plugins = []

    if include_self:
        found_plugins.append(parent_plugin)

    child_plugins = getattr(parent_plugin, 'child_plugin_instances', None) or []

    for plugin in child_plugins:
        found_nested_plugins = get_nested_plugins(plugin, include_self=True)
        found_plugins.extend(found_nested_plugins)

    return found_plugins


def get_plugin_tree(model, **kwargs):
    """
    Plugins in django CMS are highly related to a placeholder.

    This function builds a plugin tree for a plugin with no placeholder context.

    Makes as many database queries as many levels are in the tree.

    This is ok as forms shouldn't form very deep trees.
    """
    plugin = model.objects.get(**kwargs)
    plugin.parent = None
    current_level = [plugin]
    plugin_list = [plugin]
    while get_next_level(current_level).exists():
        current_level = get_next_level(current_level)
        current_level = downcast_plugins(current_level)
        plugin_list += current_level
    return build_plugin_tree(plugin_list)[0]


def get_next_level(current_level):
    all_plugins = get_cmsplugin_queryset()
    return all_plugins.filter(parent__in=[x.pk for x in current_level])


def add_form_error(form, message, field=NON_FIELD_ERRORS):
    try:
        form._errors[field].append(message)
    except KeyError:
        form._errors[field] = form.error_class([message])


def find_plugin_form(parent):
    """Return parent plugin if it is a Form type, or if not, return None."""
    while parent is not None:
        if parent.plugin_type in ('FormPlugin', 'EmailNotificationForm'):
            return parent
        parent = parent.get_parent()
    return parent


def get_form_fields_names(instance, plugin_form):
    """Return form field names."""
    names = []
    if plugin_form is None:
        return names
    for obj in plugin_form.get_descendants():
        plugin_inst = obj.get_plugin_instance()[0]
        if plugin_inst and instance.pk != plugin_inst.pk and getattr(plugin_inst, "unique_field_name", False):
            names.append(plugin_inst.name)
    return names


def make_unique_name(request, instance, field_names):
    """Make unique name that is not in field_names array."""
    unique_field_name = instance.name
    while unique_field_name in field_names:
        unique_field_name += "_"
    text = _("The field '{}' has been renamed to '{}', because such a name is already in the form.")
    message = text.format(instance.name, unique_field_name)
    messages.success(request, message)
    return unique_field_name


def rename_field_name(request, operation, plugin=None, *args, **kwargs):
    """Rename the field name if it already exists in the form."""
    if operation in (MOVE_PLUGIN, PASTE_PLUGIN):
        instance = plugin.get_plugin_instance()[0]
        if getattr(instance, "unique_field_name", False):
            field_names = get_form_fields_names(instance, find_plugin_form(instance.get_parent()))
            if instance.name in field_names:
                instance.name = make_unique_name(request, instance, field_names)
                instance.save()
