from django import template

register = template.Library()


@register.filter
def attribs(value):
    return dir(value)
