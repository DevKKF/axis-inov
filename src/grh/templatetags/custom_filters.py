
from django import template
import re

register = template.Library()

@register.filter(name='startswith')
def startswith(value, arg):
    return value.startswith(arg)


@register.filter(name='format_amount')
def format_amount(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        pass
    return '{:,}'.format(value).replace(',', ' ')


@register.filter(name='add_if_numeric_or_append_text')
def add_if_numeric_or_append_text(value, text):
    if isinstance(value, (int, float)):
        return f"{value}{text}"
    else:
        number = re.findall(r'\d+', value)
        if number:
            return f"{number[0]}{text}"
        else:
            return f"{value}{text}"


@register.filter
def email_mask(email):
    # application du masque sur l'email pour cacher les caractères exempla : a.*****i@inov.africa
    begin_email = email[:email.index('@')]
    if len(begin_email) < 6:
        return email[:2] + '*****' + email[len(begin_email)-1] + email[email.index('@'):]
    return email[:4] + '*****' + email[len(begin_email)-1] + email[email.index('@'):]