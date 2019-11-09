import sys
from distutils.version import LooseVersion
from unittest import skipIf, skipUnless

from django import VERSION as DJANGO_VERSION
from django.urls import clear_url_caches

import cms
from cms.api import add_plugin, create_page
from cms.appresolver import clear_app_resolvers
from cms.test_utils.testcases import CMSTestCase


# These means "less than or equal"
DJANGO_111 = DJANGO_VERSION[:2] >= (1, 11)
CMS_3_6 = LooseVersion(cms.__version__) < LooseVersion('4.0')


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
        try:
            self.placeholder = self.page.placeholders.get(slot='content')
        except AttributeError:
            self.placeholder = self.page.get_placeholders('en').get(slot='content')

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
        if CMS_3_6:
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

    @skipUnless(DJANGO_111, 'Django>=1.11')
    def test_form_view_and_submission_with_apphook_django_gte_111(self):
        if CMS_3_6:
            public_page = self.page.publisher_public
        else:
            public_page = self.page
        try:
            public_placeholder = public_page.placeholders.first()
        except AttributeError:
            public_placeholder = public_page.get_placeholders('en').first()

        public_page_form_plugin = (
            public_placeholder
            .cmsplugin_set
            .filter(plugin_type='FormPlugin')
            .first()
        )
        response = self.client.get(self.page.get_absolute_url('en'))

        input_string = '<input type="hidden" name="form_plugin_id" value="{}"'
        self.assertContains(response, input_string.format(public_page_form_plugin.id))  # noqa: E501

        response = self.client.post(self.page.get_absolute_url('en'), {
            'form_plugin_id': public_page_form_plugin.id,
        })
        self.assertRedirects(response, self.redirect_url, fetch_redirect_response=False)  # noqa: E501

    @skipIf(DJANGO_111, 'Django<1.11')
    def test_form_view_and_submission_with_apphook_django_lt_111(self):
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

        input_string = '<input type="hidden" name="form_plugin_id" value="{}"'
        self.assertContains(response, input_string.format(public_page_form_plugin.id))  # noqa: E501

        response = self.client.post(self.page.get_absolute_url('en'), {
            'form_plugin_id': public_page_form_plugin.id,
        })
        self.assertRedirects(response, self.redirect_url, fetch_redirect_response=False)  # noqa: E501

    def test_view_submit_one_form_instead_multiple(self):
        """Test checks if only one form is send instead of multiple on page together"""
        page = create_page(
            'multiple forms',
            'test_page.html',
            'en',
            published=True,
            apphook='FormsApp',
        )
        placeholder = page.placeholders.get(slot='content')

        form_plugin = add_plugin(
            placeholder,
            'FormPlugin',
            'en',
        )  # noqa: E501

        add_plugin(
            placeholder,
            'EmailField',
            'en',
            name='email_1',
            required=True,
            target=form_plugin,
            label='Submit',
        )

        add_plugin(
            placeholder,
            'SubmitButton',
            'en',
            target=form_plugin,
            label='Submit',
        )

        form_plugin.action_backend = 'default'
        form_plugin.save()

        plugin_data2 = {
            'redirect_type': 'redirect_to_url',
            'url': 'https://google.com/',
        }

        form_plugin2 = add_plugin(
            placeholder,
            'FormPlugin',
            'en',
            **plugin_data2
        )  # noqa: E501

        add_plugin(
            placeholder,
            'SubmitButton',
            'en',
            target=form_plugin2,
            label='Submit',
        )

        form_plugin2.action_backend = 'default'
        form_plugin2.save()

        page.publish('en')
        self.reload_urls()
        self.apphook_clear()

        response = self.client.post(page.get_absolute_url('en'), {
            'form_plugin_id': form_plugin2.id,
            'email_1': 'test@test',
        })
        self.assertRedirects(response, plugin_data2['url'], fetch_redirect_response=False)  # noqa: E501

    def test_view_submit_one_valid_form_instead_multiple(self):
        """Test checks if only one form is validated instead multiple on a page"""
        page = create_page(
            'multiple forms',
            'test_page.html',
            'en',
            published=True,
            apphook='FormsApp',
        )
        placeholder = page.placeholders.get(slot='content')

        form_plugin = add_plugin(
            placeholder,
            'FormPlugin',
            'en',
        )  # noqa: E501

        add_plugin(
            placeholder,
            'EmailField',
            'en',
            name='email_1',
            required=True,
            target=form_plugin,
        )

        add_plugin(
            placeholder,
            'SubmitButton',
            'en',
            target=form_plugin,
            label='Submit',
        )

        form_plugin.action_backend = 'default'
        form_plugin.save()

        form_plugin2 = add_plugin(
            placeholder,
            'FormPlugin',
            'en',
        )  # noqa: E501

        add_plugin(
            placeholder,
            'EmailField',
            'en',
            name='email_2',
            required=True,
            target=form_plugin2,
        )

        add_plugin(
            placeholder,
            'SubmitButton',
            'en',
            target=form_plugin2,
            label='Submit',
        )

        form_plugin2.action_backend = 'default'
        form_plugin2.save()

        page.publish('en')
        self.reload_urls()
        self.apphook_clear()

        response = self.client.post(page.get_absolute_url('en'), {
            'form_plugin_id': form_plugin2.id,
            'email_2': 'test@test',
        })

        email_field = '<input type="email" name="{name}"'
        self.assertContains(response, email_field.format(name='email_1'))
        self.assertContains(response, email_field.format(name='email_2'))
