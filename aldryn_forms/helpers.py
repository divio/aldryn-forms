# -*- coding: utf-8 -*-
from cms.cms_plugins import AliasPlugin


def get_user_name(user):
    try:
        name = user.get_full_name()
    except AttributeError:
        # custom user model
        name = ''
    return name


def is_form_element(plugin):
    # import here due because of circular imports
    from .cms_plugins import FormElement

    # cms_plugins.CMSPlugin subclass
    cms_plugin = plugin.get_plugin_class_instance(None)
    is_orphan_plugin = cms_plugin.model != plugin.__class__
    plugin_class = plugin.get_plugin_class()
    if plugin.get_plugin_class() == AliasPlugin:
        plugin_class = plugin.plugin.get_plugin_class()
    is_element_subclass = issubclass(plugin_class, FormElement)
    return (not is_orphan_plugin) and is_element_subclass
