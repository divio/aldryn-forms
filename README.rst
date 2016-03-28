================
Aldryn Forms App
================

Aldryn Forms allows you to build flexible HTML forms for your `Aldryn <http://aldryn.com>`_ and `django CMS 
<http://www.django-cms.org>`_ projects, and to integrate them directly in your pages.

Forms can be assembled using the form builder, with the familiar simple drag-and-drop interface of the django CMS
plugin system.

Submitted data is stored in the Django database, and can be explored and exported using the admin, while forms can 
be configured to send a confirmation message to users.

Installation
============

Aldryn Platform Users
---------------------

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``Forms`` app.

Redeploy the site.

Upgrading from < 2.0
====================
Version 2.0 introduced a new model for form data storage called ``FormSubmission``.
The old ``FormData`` model has been deprecated.
Although the ``FormData`` model's data is still accessible through the admin, all new form data will be stored in the new
``FormSubmission`` model.

Manuall Installation
--------------------

Run ``pip install aldryn-forms``.

Update ``INSTALLED_APPS`` with ::

    INSTALLED_APPS = [
        …
        'absolute',
        'aldryn_forms',
        'aldryn_forms.contrib.email_notifications',
        'captcha',
        'emailit',
        'filer',
        …
    ]

Configure ``aldryn-boilerplates`` (https://pypi.python.org/pypi/aldryn-boilerplates/).

To use the old templates, set ``ALDRYN_BOILERPLATE_NAME='legacy'``.
To use https://github.com/aldryn/aldryn-boilerplate-standard (recommended, will be renamed to
``aldryn-boilerplate-bootstrap3``) set ``ALDRYN_BOILERPLATE_NAME='bootstrap3'``.

Also ensure you define an `e-mail backend <https://docs.djangoproject.com/en/dev/topics/email/#dummy-backend>`_ for your app.


Creating a Form
===============

You can create forms in the admin interface now. Search for the label ``Aldryn_Forms``.

Create a CMS page and install the ``Forms`` app there (choose ``Forms`` from the ``Advanced Settings -> Application`` dropdown).

Now redeploy/restart the site again.

The above CMS site has become a forms POST landing page – a place where submission errors get displayed if there are any.


Available Plug-ins
==================

``Form`` plugin lets you embed certain forms on a CMS page.

``Fieldset`` groups fields.

``Text Field`` renders text input.

``Text Area Field`` renders text input.

``Yes/No Field`` renders checkbox.

``Select Field`` renders single select input.

``Multiple Select Field`` renders multiple checkboxes.

``File field`` renders a file upload input.

``Image field`` same as ``file field`` but validates that the uploaded file is an image.
