from django.db import models
from django.conf import settings

class Store(models.Model):
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'في انتظار الموافقة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'store_owner'},
        related_name='stores'
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'user_type': 'admin'},
        related_name='approved_stores'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.store.name})"

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  # إجمالي الكمية (يتم حسابه تلقائياً)
    sizes = models.CharField(max_length=200, blank=True, help_text="مثال: S,M,L,XL")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.store.name}"
    
    def get_total_stock(self):
        """حساب إجمالي الكمية من جميع المقاسات"""
        return sum(size_stock.stock for size_stock in self.size_stocks.all())
    
    def get_size_stock(self, size):
        """الحصول على كمية مقاس معين"""
        try:
            size_stock = self.size_stocks.get(size=size)
            return size_stock.stock
        except ProductSizeStock.DoesNotExist:
            return 0


class ProductSizeStock(models.Model):
    """نموذج لحفظ الكميات حسب المقاس لكل منتج"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='size_stocks')
    size = models.CharField(max_length=20, help_text="مثال: S, M, L, XL, XXL")
    stock = models.PositiveIntegerField(default=0, help_text="الكمية المتاحة لهذا المقاس")
    
    class Meta:
        unique_together = ('product', 'size')  # منع تكرار نفس المقاس لنفس المنتج
        verbose_name = 'كمية المقاس'
        verbose_name_plural = 'كميات المقاسات'
    
    def __str__(self):
        return f"{self.product.name} - {self.size}: {self.stock}"
    
    # models.py
class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    size = models.CharField(max_length=20, blank=True, null=True, help_text="المقاس المباع")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # سعر الوحدة وقت الشراء
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        product_name = self.product.name if self.product else "منتج محذوف"
        size_text = f" ({self.size})" if self.size else ""
        return f"{product_name}{size_text} - {self.buyer.username} - {self.store.name}"



# نموذج السلة
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) 

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, blank=True, null=True, help_text="المقاس المختار")
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        size_text = f" ({self.size})" if self.size else ""
        return f"{self.quantity} x {self.product.name}{size_text}"
    
    class Meta:
        unique_together = ('cart', 'product', 'size')  # منع تكرار نفس المنتج بنفس المقاس في السلة


# نموذج المتاجر المفضلة
class FavoriteStore(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_stores'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'store')  # منع إضافة نفس المتجر مرتين
        verbose_name = 'متجر مفضل'
        verbose_name_plural = 'المتاجر المفضلة'

    def __str__(self):
        return f"{self.user.username} - {self.store.name}"
