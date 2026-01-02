from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Product, CartItem


@receiver(pre_delete, sender=Product)
def delete_product_from_cart(sender, instance, **kwargs):
    """
    حذف المنتج من جميع السلات عند حذفه من قبل صاحب المتجر
    هذا يضمن التزامن بين حذف المنتج وحذفه من سلات المشترين
    """
    # حذف جميع عناصر السلة المرتبطة بهذا المنتج
    cart_items = CartItem.objects.filter(product=instance)
    count = cart_items.count()
    if count > 0:
        cart_items.delete()
        # يمكن إضافة رسالة أو سجل هنا إذا لزم الأمر

