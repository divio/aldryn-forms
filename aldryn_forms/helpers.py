# -*- coding: utf-8 -*-


def is_form_element(plugin):
    # import here due because of circular imports
    from .cms_plugins import FormElement

    # cms_plugins.CMSPlugin subclass
    cms_plugin = plugin.get_plugin_class_instance(None)
    is_orphan_plugin = cms_plugin.model != plugin.__class__
    is_element_subclass = issubclass(plugin.get_plugin_class(), FormElement)
    return (not is_orphan_plugin) and is_element_subclass
