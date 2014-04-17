# -*- coding: utf-8 -*-
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.translation import ugettext_lazy as _


class MinChoicesValidator(MinLengthValidator):

    message = _('You have to choose at least %(limit_value)d options (chosen %(show_value)d).')
    code = 'min_choices'


class MaxChoicesValidator(MaxLengthValidator):

    message = _('You can\'t choose more than %(limit_value)d options (chosen %(show_value)d).')
    code = 'max_choices'
