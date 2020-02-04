import sys
from distutils.version import LooseVersion
from unittest import skipIf, skipUnless
from urllib.parse import urlencode

from django import VERSION as DJANGO_VERSION
from django.urls import clear_url_caches

import cms
from cms.api import add_plugin, create_page
from cms.appresolver import clear_app_resolvers
from cms.test_utils.testcases import (
    URL_CMS_PLUGIN_ADD, URL_CMS_PLUGIN_EDIT, URL_CMS_PLUGIN_MOVE, CMSTestCase,
)

from aldryn_forms import models as aldryn_models


# These means "less than or equal"
DJANGO_111 = DJANGO_VERSION[:2] >= (1, 11)
CMS_3_6 = LooseVersion(cms.__version__) < LooseVersion('4.0')


class InitAppUrlsMixin:

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


class SubmitFormViewTest(InitAppUrlsMixin, CMSTestCase):

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


class UniqueFieldNameTest(InitAppUrlsMixin, CMSTestCase):

    def setUp(self):
        super(UniqueFieldNameTest, self).setUp()
        add_plugin(self.placeholder, 'TextField', 'en', target=self.form_plugin, name="first_name", label="First name")
        add_plugin(self.placeholder, 'TextField', 'en', target=self.form_plugin, name="last_name", label="Last name")
        fldset = add_plugin(self.placeholder, 'Fieldset', 'en', target=self.form_plugin, legend="Private")
        self.email = add_plugin(fldset.placeholder, 'EmailField', 'en', target=fldset, name="email", label="E-mail")
        if CMS_3_6:
            self.page.publish('en')

    def _get_params(self):
        return {
            "placeholder_id": self.form_plugin.placeholder.pk,
            "plugin_type": "EmailField",
            "cms_path": self.page.get_absolute_url(),
            "plugin_language": "en",
            "plugin_parent": self.form_plugin.pk,
        }

    def test_add_field(self):
        url = "{}?{}".format(URL_CMS_PLUGIN_ADD, urlencode(self._get_params()))
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, {"name": "alt-email"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="alt-email").exists())

    def test_add_field_with_duplicate_name(self):
        url = "{}?{}".format(URL_CMS_PLUGIN_ADD, urlencode(self._get_params()))
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, {"name": "email"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email_").exists())

    def test_change_field(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}{}/?{}".format(URL_CMS_PLUGIN_EDIT, self.email.pk, urlencode(params))
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, {"name": "email-2"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email-2").exists())

    def test_change_field_with_duplicate_name(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}{}/?{}".format(URL_CMS_PLUGIN_EDIT, self.email.pk, urlencode(params))
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, {"name": "last_name"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['adminform'].errors, {'name': [
            'This field name is already used in the form. Please select another.']})

    def _get_move_params(self, plugin):
        return {
            "placeholder_id": self.form_plugin.placeholder.pk,
            "plugin_id": plugin.pk,
            "plugin_parent": self.form_plugin.pk,
            "target_language": "en",
        }

    def test_move_field(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}?{}".format(URL_CMS_PLUGIN_MOVE, urlencode(params))
        new_field = add_plugin(self.placeholder, 'EmailField', 'en', name="email-2", label="E-mail 2")
        data = self._get_move_params(new_field)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email-2").exists())

    def test_move_field_with_duplicate_name(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}?{}".format(URL_CMS_PLUGIN_MOVE, urlencode(params))
        new_field = add_plugin(self.placeholder, 'EmailField', 'en', name="email", label="E-mail")
        data = self._get_move_params(new_field)
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email_").exists())

    def test_paste_field(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}?{}".format(URL_CMS_PLUGIN_MOVE, urlencode(params))
        new_field = add_plugin(self.placeholder, 'EmailField', 'en', name="email-2", label="E-mail 2")
        data = self._get_move_params(new_field)
        data['move_a_copy'] = True
        data['plugin_order[]'] = '__COPY__'
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email-2").exists())

    def test_paste_field_with_duplicate_name(self):
        params = {"cms_path": self.page.get_absolute_url()}
        url = "{}?{}".format(URL_CMS_PLUGIN_MOVE, urlencode(params))
        new_field = add_plugin(self.placeholder, 'EmailField', 'en', name="email", label="E-mail")
        data = self._get_move_params(new_field)
        data['move_a_copy'] = True
        data['plugin_order[]'] = '__COPY__'
        superuser = self.get_superuser()
        with self.login_user_context(superuser):
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(aldryn_models.EmailFieldPlugin.objects.filter(name="email_").exists())
