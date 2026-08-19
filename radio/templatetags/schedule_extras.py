from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Look up dictionary[key] in a template, where key is itself a variable
    (Django's built-in dot notation only supports literal keys)."""
    if dictionary is None:
        return None
    return dictionary.get(key)
