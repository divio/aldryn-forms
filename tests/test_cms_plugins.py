from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase

from aldryn_forms.models import FormSubmission


class FormPluginTestCase(CMSTestCase):
    def setUp(self):
        super(FormPluginTestCase, self).setUp()

        self.page = create_page('test page', 'INHERIT', 'en', published=True)
        self.placeholder = self.page.placeholders.get()

        add_plugin(self.placeholder, 'FormPlugin', 'en')
        self.form_plugin = self.placeholder.cmsplugin_set.get().aldryn_forms_formplugin
        self.form_plugin.redirect_type = 'redirect_to_url'
        self.form_plugin.url = 'http://www.google.com'
        self.form_plugin.save()

        add_plugin(self.placeholder, 'SubmitButton', 'en', target=self.form_plugin)

    def test_form_submission_default_storage(self):
        self.form_plugin.storage_backend = 'default'
        self.form_plugin.save()
        self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 1)

    def test_form_submission_no_storage(self):
        self.form_plugin.storage_backend = 'no_storage'
        self.form_plugin.save()
        self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)


class EmailNotificationFormPluginTestCase(CMSTestCase):
    def setUp(self):
        super(EmailNotificationFormPluginTestCase, self).setUp()

        self.page = create_page('test page', 'INHERIT', 'en', published=True)
        self.placeholder = self.page.placeholders.get()

        add_plugin(self.placeholder, 'EmailNotificationForm', 'en')
        self.form_plugin = self.placeholder.cmsplugin_set.get().aldryn_forms_formplugin
        self.form_plugin.redirect_type = 'redirect_to_url'
        self.form_plugin.url = 'http://www.google.com'
        self.form_plugin.save()

        add_plugin(self.placeholder, 'SubmitButton', 'en', target=self.form_plugin)

    def test_form_submission_default_storage(self):
        self.form_plugin.storage_backend = 'default'
        self.form_plugin.save()
        self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 1)

    def test_form_submission_no_storage(self):
        self.form_plugin.storage_backend = 'no_storage'
        self.form_plugin.save()
        self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
