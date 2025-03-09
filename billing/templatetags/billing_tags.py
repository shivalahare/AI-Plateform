from django import template

register = template.Library()

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces and capitalize each word"""
    return value.replace('_', ' ').title()

@register.filter
def percentage(value, max_value):
    try:
        return int((value / max_value) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
