from django import template

register = template.Library()


@register.filter
def unread_count(user):
    """Count unread notifications for a user"""
    if user and user.is_authenticated:
        return user.notifications.filter(is_read=False).count()
    return 0
