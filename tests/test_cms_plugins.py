from django.contrib.auth.models import User
from django.core import mail

from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase

from tests.test_views import CMS_3_6

from aldryn_forms.models import FormSubmission


class FormPluginTestCase(CMSTestCase):
    def setUp(self):
        super(FormPluginTestCase, self).setUp()

        self.page = create_page('test page', 'test_page.html', 'en', published=True)
        try:
            self.placeholder = self.page.placeholders.get(slot='content')
        except AttributeError:
            self.placeholder = self.page.get_placeholders('en').get(slot='content')
        self.user = User.objects.create_superuser('username', 'email@example.com', 'password')

        plugin_data = {
            'redirect_type': 'redirect_to_url',
            'url': 'http://www.google.com',
        }
        self.form_plugin = add_plugin(self.placeholder, 'FormPlugin', 'en', **plugin_data)
        self.form_plugin.recipients.add(self.user)

        add_plugin(self.placeholder, 'SubmitButton', 'en', target=self.form_plugin)

    def test_form_submission_default_action(self):
        self.form_plugin.action_backend = 'default'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)

    def test_form_submission_email_action(self):
        self.form_plugin.action_backend = 'email_only'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)

    def test_form_submission_no_action(self):
        self.form_plugin.action_backend = 'none'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)


class EmailNotificationFormPluginTestCase(CMSTestCase):
    def setUp(self):
        super(EmailNotificationFormPluginTestCase, self).setUp()

        self.page = create_page('test page', 'test_page.html', 'en', published=True)
        try:
            self.placeholder = self.page.placeholders.get(slot='content')
        except AttributeError:
            self.placeholder = self.page.get_placeholders('en').get(slot='content')
        self.user = User.objects.create_superuser('username', 'email@example.com', 'password')

        plugin_data = {
            'redirect_type': 'redirect_to_url',
            'url': 'http://www.google.com',
        }
        self.form_plugin = add_plugin(self.placeholder, 'EmailNotificationForm', 'en', **plugin_data)
        self.form_plugin.email_notifications.create(to_user=self.user, theme='default')

        add_plugin(self.placeholder, 'SubmitButton', 'en', target=self.form_plugin)

    def test_form_submission_default_action(self):
        self.form_plugin.action_backend = 'default'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)

    def test_form_submission_email_action(self):
        self.form_plugin.action_backend = 'email_only'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)

    def test_form_submission_no_action(self):
        self.form_plugin.action_backend = 'none'
        self.form_plugin.save()
        if CMS_3_6:
            self.page.publish('en')

        response = self.client.post(self.page.get_absolute_url('en'), {})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(FormSubmission.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 0)
