#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'tests',
        'aldryn_forms.contrib.email_notifications',
        'djangocms_text_ckeditor',
        'absolute',
        'captcha',
        'easy_thumbnails',
        'emailit',
        'filer',
    ],
    'ALLOWED_HOSTS': [
        'localhost'
    ],
    'CMS_LANGUAGES': {
        1: [{
            'code': 'en',
            'name': 'English',
        }]
    },
    'CMS_TEMPLATES': (
        ('test_fullwidth.html', 'Fullwidth'),
        ('test_page.html', 'Normal page'),
    ),
    'LANGUAGE_CODE': 'en',
    'EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend',
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_forms')


if __name__ == '__main__':
    run()
