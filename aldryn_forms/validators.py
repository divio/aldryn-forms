import os
from email.utils import parseaddr

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator, MinLengthValidator, validate_email,
)
from django.utils.translation import gettext_lazy as _

from aldryn_forms.utils import serialize_delimiter_separated_values_string


def generate_file_extension_validator(allowed_extensions_str: str = ""):
    allowed_extensions = serialize_delimiter_separated_values_string(
        allowed_extensions_str, delimiter=",", strip=True, lower=True
    )

    if not allowed_extensions:
        return lambda value: None

    allowed_extensions = [
        extension if extension.startswith(".") else f".{extension}"
        for extension in allowed_extensions
    ]

    def validator(value):
        extension = os.path.splitext(value.name)[1]  # [0] returns path+filename
        if not extension.lower() in allowed_extensions:
            raise ValidationError(
                _(f"File extension '{extension}' is not allowed for this field."),
                code="invalid_extension",
            )

    return validator

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


class MinChoicesValidator(MinLengthValidator):

    message = _('You have to choose at least %(limit_value)d options (chosen %(show_value)d).')
    code = 'min_choices'


class MaxChoicesValidator(MaxLengthValidator):

    message = _('You can\'t choose more than %(limit_value)d options (chosen %(show_value)d).')
    code = 'max_choices'
