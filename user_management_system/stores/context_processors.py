from .models import Store, Cart, Sale

def store_context(request):
    """
    يضيف أول متجر مملوك للمستخدم إلى السياق (إذا كان المستخدم صاحب متجر)
    بالإضافة إلى عدد العناصر في السلة وعدد المبيعات
    """
    context = {
        'cart_item_count': 0,
        'store_sales_count': 0
    }
    
    if request.user.is_authenticated:
        try:
            # إضافة المتاجر
            stores = Store.objects.filter(owner=request.user)
            if stores.exists():
                store = stores.first()
                context['store'] = store
                context['user_stores'] = stores
                
                # إضافة عدد المبيعات لصاحب المتجر
                if hasattr(request.user, 'is_store_owner') and request.user.is_store_owner():
                    sales_count = Sale.objects.filter(store=store, product__isnull=False).count()
                    context['store_sales_count'] = sales_count
            
            # إضافة عدد العناصر في السلة للمستخدم العادي
            if not (hasattr(request.user, 'is_store_owner') and request.user.is_store_owner()):
                try:
                    cart = Cart.objects.get(user=request.user, is_active=True)
                    cart_item_count = cart.items.count()
                    context['cart_item_count'] = cart_item_count
                except Cart.DoesNotExist:
                    context['cart_item_count'] = 0
        except Exception:
            # في حالة حدوث أي خطأ، نعيد القيم الافتراضية
            pass
    
    return context
