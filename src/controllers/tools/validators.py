from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

#https://docs.djangoproject.com/en/2.2/ref/validators/

def validators_throw_error_basic(msg, value):
    raise ValidationError(
            _(' \'%(value)s\' ' + msg),
            params={'value': value}
        )

def validator_no_espacios(value):
    if not value.find(' ') == -1:
        validators_throw_error_basic('no deberia contener espacios en blanco', value)
