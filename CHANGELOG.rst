Changelog
=========

3.0.0 (unreleased)
-------------------
* New fields were added to the ``FieldPluginBase`` class, as a result, any model
  that inherits from it will need to update its migrations.
* Added new ``name`` field to customize a field's name attribute.
* Added a ``position`` field to the ``Option`` model for ordered choices support.
* Renamed the form's ``page`` field to ``redirect_page``.
* Introduced the ``BaseForm`` class to make it easier to create custom form types.
* Introduced support for customizing the input's tag ``type`` attribute.
* Introduced new ``Phone``, ``Number`` and ``Hidden`` fields.
* Introduced custom attributes support for the forms and fields.
* Refactored storage backends engine to be 'action backends'

2.3.0 (2017-12-19)
-------------------
* Fixed bootstrap3 templates missing custom classes
* Added support for custom storage per form

2.2.9 (2017-10-09)
------------------
* Added reply-to email header support to advanced form.
* Updated translations

2.2.8 (2017-09-04)
------------------
* Fixed a bug in the bootstrap3 template which prevented the multiselectfield
  from submitting values to the server.

2.2.7 (2017-08-29)
------------------
* Updated translations

2.2.6 (2017-08-22)
------------------
* Updated translations

2.2.5 (2017-08-21)
------------------
* Marked several strings as translatable
* Updated translations

2.2.4 (2017-07-05)
------------------
* Fixed AttributeError introduced by new migration
* Fixed a python 3 compatibility issue

2.2.3 (2017-07-04)
------------------
* Fixed django 1.10 incompatibility in form submit view
* Add missing permissions for contrib.EmailNotificationFormPlugin

2.2.2 (2017-05-16)
------------------
* Fix multiple checkbox option widget template

2.2.1 (2017-03-20)
------------------
* Allow FieldPlugins to set a max_length of more than 255 chars
* Allow various fields (name, label, ..,) to be longer (255 chars)

2.2.0 (2017-03-15)
------------------
* Django 1.10 support
* Dropped Django < 1.7 support (south migrations removed)

2.1.3 (2016-09-05)
------------------
* Added missing `control-label`` classes in bootstrap templates
* Fixed related_name inconsistency with django CMS 3.3.1
* Dropped support for djangoCMS < 3.2
* Introduced support for djangoCMS 3.4.0

2.1.2 (2016-06-17)
------------------
* Added Transifex support
* Pulled translations from Transifex (German)
* Adapted translation strings in templates

2.1.1 (2016-03-09)
------------------
* Fixed image upload field on Django >= 1.8

2.1.0 (2016-02-18)
------------------
* Removed deprecated ``formdata``
* Renamed ``Email Notification Form`` to ``Form (Advanced)``
* Optimized admin export templates
* Add stripped default django templates to ``/aldryn_forms/templates``
* Implement "Advanced Settings" when configuring plugins
* Adapt default setting ``show_all_recipients`` for aldryn users
* Removed not required options from form fields
* Set default for "Field is required" to ``False``
* Fix Django 1.9 issues

2.0.4 (2016-01-20)
------------------
* Show label when using radio fields
* Show help text when using radio fields
* Python 3 compatibility fixes

2.0.3 (2016-01-04)
------------------
* Refactored form data and form submission export logic.
* Fixes bug in email notifications not respecting confirmation flag.
* Updates po files.

2.0.2 (2015-12-17)
------------------
* Remove "South" dependency from setup.py

2.0.1 (2015-12-14)
------------------
* Fixes minor bug in form data export redirect.

2.0.0 (2015-12-14)
------------------
* Refactor the FormData model into FormSubmission.
* FormData is now a deprecated model.
* Form exports are now limited to one language at a time.

1.0.3 (2015-12-08)
------------------
* Fixes critical bug with nested plugins.

1.0.2 (2015-12-08)
------------------
* Fixes plugin ordering bug.
* Fixes TypeError on some fields because of the validator.
* Marks some strings as translatable.

1.0.1 (2015-11-26)
------------------
* Allows for custom forms to opt out of a success message.

1.0.0 (2015-11-03)
------------------
* Stable release

0.6.0 (2015-10-14)
------------------
* adds validator on max_length fields
* cms 3.1 migration compatibility fix

0.5.1 (2015-09-29)
------------------
* cms 3.1 compatibility fix

0.5.0 (2015-08-19)
------------------
* added django 1.7 & 1.8 compatibility
* fixes AttributeError with orphan plugins

0.4.1 (2015-07-10)
------------------
* added notification config class to support custom text variables
* allow disabling email html version
* allow hiding of email body txt format field
* fixed bug with serialized boolean value

0.4.0 (2015-07-02)
------------------
* added email notification contrib app which includes new email notification form
* added html version to admin notification email text
* changed the users_notified field to a text field to support non user recipients
* hides the captcha field/value from serialized data
* cleaned up field serialization logic.

0.3.3 (2015-05-29)
------------------
* added support for default values in selectfields, multiselectfields and radioselects (bootstrap).
* fixed empty values in select options

0.3.2 (2015-05-19)
------------------
* bootstrap3 support
* added bootstrap markup templates for all field-types

0.3.0 (2015-03-02)
------------------
* multi-boilerplate support
* new requirement: aldryn-boilerplates (needs configuration)
