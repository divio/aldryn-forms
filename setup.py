from setuptools import find_packages, setup

from aldryn_forms import __version__


REQUIREMENTS = [
    'django>=2.0',
    'aldryn-boilerplates>=0.7.5',
    'django-cms>=3.5',
    'django-emailit',
    'djangocms-text-ckeditor',
    'djangocms-attributes-field>=1.0.0',
    'django-tablib',
    'tablib',
    'pillow',
    'django-filer',
    'django-sizefield',
    'six>=1.0',
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Framework :: Django',
    'Framework :: Django :: 2.2',
    'Programming Language :: Python',
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
    extras_require={
        'captcha': ['django-simple-captcha'],
    },
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
