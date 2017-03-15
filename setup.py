# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_forms import __version__

REQUIREMENTS = [
    'django-cms>=3.2',
    'django-emailit',
    'djangocms-text-ckeditor',
    'django-simple-captcha',
    'django-tablib',
    'tablib',
    'pillow',
    'django-filer',
    'django-sizefield',
    'aldryn-boilerplates>=0.6',
    'Django>=1.7',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-forms',
    version=__version__,
    description='Create forms and embed them on CMS pages',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-forms',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)
