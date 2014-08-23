# -*- coding: utf-8 -*-
from django.db import models
from django.forms.forms import NON_FIELD_ERRORS

from cms.utils.moderator import get_cmsplugin_queryset
try:
    from cms.utils.plugins import downcast_plugins, build_plugin_tree
except ImportError:
    from cms.plugins.utils import downcast_plugins, build_plugin_tree


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
        current_level = downcast_plugins(queryset=current_level)
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


def get_form_render_data(form):
    form_data = []
    for field in form.visible_fields():
        value = form.cleaned_data[field.name]
        if isinstance(value, models.query.QuerySet):
            value = ', '.join(map(unicode, value))
        elif value is None:
            value = '-'
        name = field.label if field.label else field.name
        form_data.append((name, value))
    return form_data
