# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from djangocms_translations import __version__
from aldryn_forms import __version__


REQUIREMENTS = [
    'aldryn-boilerplates>=0.8.0',
    'django-cms>=3.4.5',
    'django-emailit>=0.2.4',
    'djangocms-text-ckeditor>=3.7.0',
    'djangocms-attributes-field>=1.0.0',
    'django-simple-captcha',
    'django-tablib',
    'tablib',
    'pillow',
    'django-filer>=1.4.2',
    'openpyxl<=2.4.9',  # 2.5.0b1 is raising "ImportError: cannot import name '__version__'"
    'Django>=1.11',
    'six>=1.0',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',

    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='aldryn-forms',
    version=__version__,
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-forms',
    license='BSD',
    description='Create forms and embed them on CMS pages',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
