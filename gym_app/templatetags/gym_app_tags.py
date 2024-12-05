# gym_app/templatetags/gym_app_tags.py

from django import template
from gym_app.models import Profile

register = template.Library()

@register.filter
def get_profile(user):
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None
