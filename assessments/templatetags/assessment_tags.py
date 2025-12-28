from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    try:
        if hasattr(dictionary, 'get'):
            return dictionary.get(key)
        return dictionary[key]
    except (KeyError, TypeError, AttributeError):
        return None

