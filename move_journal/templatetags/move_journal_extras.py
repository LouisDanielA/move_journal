from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='get_name')
@stringfilter
def get_name(value):
    """Получаю название поля"""
    value= value.split('/')[-1]
    return value