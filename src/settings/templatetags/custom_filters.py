from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)  # Convert to numbers before multiplying
    except (ValueError, TypeError):
        return 0


@register.filter
def add(value, arg):
    try:
        return float(value) + float(arg)  # Convert to numbers before multiplying
    except (ValueError, TypeError):
        return 0
