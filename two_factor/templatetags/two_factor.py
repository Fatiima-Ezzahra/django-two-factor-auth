import re

import phonenumbers
from django import template
from django.utils.translation import gettext as _

from ..models import PhoneDevice, EmailDevice

register = template.Library()

phone_mask = re.compile('(?<=.{3})[0-9](?=.{2})')

email_mask = re.compile('(?<=.{3})[\w](?=.{4})')


@register.filter
def mask_phone_number(number):
    """
    Masks a phone number, only first 3 and last 2 digits visible.

    Examples:

    * `+31 * ******58`

    :param number: str or phonenumber object
    :return: str
    """
    if isinstance(number, phonenumbers.PhoneNumber):
        number = format_phone_number(number)
    return phone_mask.sub('*', number)


@register.filter
def format_phone_number(number):
    """
    Formats a phone number in international notation.
    :param number: str or phonenumber object
    :return: str
    """
    if not isinstance(number, phonenumbers.PhoneNumber):
        number = phonenumbers.parse(number)
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)


@register.filter
def device_action(device):
    """
    Generates an actionable text for a :class:`~two_factor.models.PhoneDevice`.

    Examples:

    * Send text message to `+31 * ******58`
    * Call number `+31 * ******58`
    """
    assert isinstance(device, PhoneDevice)
    number = mask_phone_number(format_phone_number(device.number))
    if device.method == 'sms':
        return _('Send text message to %s') % number
    elif device.method == 'call':
        return _('Call number %s') % number
    raise NotImplementedError('Unknown method: %s' % device.method)


@register.filter
def mask_email(email):
    """
    Masks an email, only first 3 and last 4 characters visible.

    Example:

    * `joh°°°°°95.co`

    :param email: str
    :return: str
    """
    return email_mask.sub('*', email)


@register.filter
def email_device_action(device):
    """
    Generates an actionable text for a :class:`~two_factor.models.EmailDevice`.

    Example:

    * Send email to `joh°°°°°95.co`
    """
    assert isinstance(device, EmailDevice)
    email = mask_email(device.email)
    if device.method == 'email':
        return _('Send email to %s') % email
    raise NotImplementedError('Unknown method: %s' % device.method)
