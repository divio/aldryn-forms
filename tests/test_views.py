import sys

from django.core.urlresolvers import clear_url_caches

from cms.api import add_plugin, create_page
from cms.appresolver import clear_app_resolvers
from cms.test_utils.testcases import CMSTestCase


class SubmitFormViewTest(CMSTestCase):

    def setUp(self):
        self.APP_MODULE = 'aldryn_forms.cms_apps.FormsApp'
        clear_app_resolvers()
        clear_url_caches()

        if self.APP_MODULE in sys.modules:
            del sys.modules[self.APP_MODULE]

        self.page = create_page(
            'tpage',
            'test_page.html',
            'en',
            published=True,
            apphook='FormsApp',
        )
        self.placeholder = self.page.placeholders.get(slot='content')
        self.redirect_url = 'http://www.google.com'

        plugin_data = {
            'redirect_type': 'redirect_to_url',
            'url': self.redirect_url,
        }
        self.form_plugin = add_plugin(self.placeholder, 'FormPlugin', 'en', **plugin_data)  # noqa: E501

        add_plugin(
            self.placeholder,
            'SubmitButton',
            'en',
            target=self.form_plugin,
            label='Submit',
        )
        self.form_plugin.action_backend = 'default'
        self.form_plugin.save()
        self.page.publish('en')

        self.reload_urls()
        self.apphook_clear()

    def tearDown(self):
        clear_app_resolvers()
        clear_url_caches()

        if self.APP_MODULE in sys.modules:
            del sys.modules[self.APP_MODULE]

        self.reload_urls()
        self.apphook_clear()

    def reload_urls(self):
        from django.conf import settings

        url_modules = [
            'cms.urls',
            self.APP_MODULE,
            settings.ROOT_URLCONF,
        ]

        clear_app_resolvers()
        clear_url_caches()

        for module in url_modules:
            if module in sys.modules:
                del sys.modules[module]

    def test_form_view_and_submission_with_apphook(self):
        public_placeholder = (
            self
            .page
            .publisher_public
            .placeholders
            .first()
        )
        public_page_form_plugin = (
            public_placeholder
            .cmsplugin_set
            .filter(plugin_type='FormPlugin')
            .first()
        )
        response = self.client.get(self.page.get_absolute_url('en'))
        self.assertContains(
            response,
            '<input type="hidden" name="form_plugin_id" value="{}"'.format(public_page_form_plugin.id),  # noqa: E501
        )

        response = self.client.post(self.page.get_absolute_url('en'), {
            'form_plugin_id': public_page_form_plugin.id,
        })
        self.assertRedirects(response, self.redirect_url, fetch_redirect_response=False)  # noqa: E501
