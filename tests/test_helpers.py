from distutils.version import LooseVersion

import cms
from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.helpers import is_form_element


CMS_3_6 = LooseVersion(cms.__version__) < LooseVersion('4.0')


class HelpersTest(CMSTestCase):

    def setUp(self):
        page = create_page('test page', 'test_page.html', 'en')
        if CMS_3_6:
            self.placeholder = page.placeholders.get(slot='content')
        else:
            self.placeholder = page.get_placeholders('en').get(slot='content')

    def test_is_form_element_is_field(self):
        plugin = add_plugin(self.placeholder, 'EmailField', 'en', name="email")
        self.assertTrue(is_form_element(plugin))

    def test_is_form_element_is_not_field(self):
        plugin = add_plugin(self.placeholder, 'TextPlugin', 'en')
        self.assertFalse(is_form_element(plugin))

    def test_is_form_element_alias_with_field(self):
        field = add_plugin(self.placeholder, 'EmailField', 'en', name="email")
        plugin = add_plugin(self.placeholder, 'AliasPlugin', 'en', plugin=field)
        self.assertTrue(is_form_element(plugin))

    def test_is_form_element_alias_without_field(self):
        field = add_plugin(self.placeholder, 'TextPlugin', 'en')
        plugin = add_plugin(self.placeholder, 'AliasPlugin', 'en', plugin=field)
        self.assertFalse(is_form_element(plugin))
