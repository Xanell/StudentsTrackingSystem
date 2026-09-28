from django import template
from Core.Enums import ROLE_LABELS
from Core.Enums import DAY_TYPE_LABELS
from Core.Enums import DAY_OFF_TYPES
register = template.Library()

@register.filter
def role_label(role):
    """{{ user.role|role_label }} -> "Ученик" вместо "student"."""
    return ROLE_LABELS.get(role, role)

@register.filter
def day_type_label(day_type):
    return DAY_TYPE_LABELS.get(day_type, day_type)

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)