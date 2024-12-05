from django import template
register = template.Library()

@register.filter
def to(value, max_value):
    """This will return a list with filled stars and empty stars."""
    try:
        value = int(value)  # Try to convert the value to an integer
    except (ValueError, TypeError):
        value = 0  # If conversion fails, default to 0
    
    filled_stars = '★' * value
    empty_stars = '☆' * (max_value - value)
    return filled_stars + empty_stars


@register.filter
def range_filter(value):
    return range(value)
