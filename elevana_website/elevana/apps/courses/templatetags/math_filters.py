from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return round(float(value) / float(arg), 2)
    except (ValueError, ZeroDivisionError):
        return None