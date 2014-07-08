================
Aldryn Forms App
================

This add-on allows you to:

- create forms
- display them on CMS pages

Installation
============

Aldryn Platrofm Users
---------------------

Choose a site you want to install the add-on to from the dashboard. Then go to ``Apps -> Install app`` and click ``Install`` next to ``Forms`` app.

Redeploy the site.

Manuall Installation
--------------------

Run ``pip install aldryn-forms``.

Update ``INSTALLED_APPS`` with ::

    INSTALLED_APPS = [
        …
        'absolute',
        'aldryn_forms',
        'captcha',
        'emailit',
        …
    ]


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
