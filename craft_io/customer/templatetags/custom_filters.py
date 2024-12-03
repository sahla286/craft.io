from django import template
register = template.Library()

@register.filter
def to(value, arg):
    # Your filter logic here
    return str(value) + str(arg)
