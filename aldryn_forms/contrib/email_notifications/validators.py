# -*- coding: utf-8 -*-
from email.utils import parseaddr

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def is_valid_recipient(recipient):
    """
    recipient - a string in any of the following formats (RFC 2822):
        name
        useremail@gmail.com
        name <useremail@mail.com>
    """
    if not recipient:
        return False

    email_address = parseaddr(recipient)[1]

    try:
        validate_email(email_address)
    except ValidationError:
        return False
    else:
        return True
