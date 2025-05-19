import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_valid_south_african_phone_number(phone_number):
    # Regular expression for South African phone numbers
    pattern = re.compile(r'^(\+27|0)[6-8][0-9]{8}$')

    if not bool(pattern.match(phone_number)):
        raise ValidationError(
            _("Phone number is not valid"), code="invalid_phone_number"
        )
