from django import template
from ..models import FavoriteStore

register = template.Library()

@register.simple_tag(takes_context=True, name='is_favorite')
def check_is_favorite(context, store_id):
    """التحقق إذا كان المتجر في قائمة المفضلة"""
    request = context.get('request')
    if request and request.user.is_authenticated:
        return FavoriteStore.objects.filter(
            user=request.user,
            store_id=store_id
        ).exists()
    return False

