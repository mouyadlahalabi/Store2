from django import template
from ..models import FavoriteProduct

register = template.Library()


@register.simple_tag(takes_context=True, name='is_product_favorite')
def is_product_favorite(context, product_id):
    request = context.get('request')
    if request and request.user.is_authenticated:
        return FavoriteProduct.objects.filter(
            user=request.user,
            product_id=product_id
        ).exists()
    return False
