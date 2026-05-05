from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

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

    @property
    def average_rating(self):
        return self.ratings.aggregate(avg=models.Avg('rating'))['avg'] or 0

    @property
    def ratings_count(self):
        return self.ratings.count()


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
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="السعر الأصلي قبل الخصم - عند تعبئته يظهر المنتج في العروض"
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  # إجمالي الكمية (يتم حسابه تلقائياً)
    sizes = models.CharField(max_length=200, blank=True, help_text="مثال: S,M,L,XL")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.store.name}"

    @property
    def average_rating(self):
        return self.ratings.aggregate(avg=models.Avg('rating'))['avg'] or 0

    @property
    def ratings_count(self):
        return self.ratings.count()
    
    def get_total_stock(self):
        """حساب إجمالي الكمية من جميع المقاسات أو الحقل stock"""
        size_total = sum(size_stock.stock for size_stock in self.size_stocks.all())
        return size_total if size_total > 0 else self.stock
    
    def is_on_offer(self):
        """هل المنتج ضمن العروض؟"""
        return self.original_price is not None and self.original_price > self.price

    def get_discount_percent(self):
        """نسبة الخصم"""
        if not self.is_on_offer():
            return 0
        return int(((float(self.original_price) - float(self.price)) / float(self.original_price)) * 100)

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


class FavoriteProduct(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'منتج مفضل'
        verbose_name_plural = 'المنتجات المفضلة'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class StoreRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='store_ratings'
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'store')
        ordering = ['-updated_at']
        verbose_name = 'تقييم متجر'
        verbose_name_plural = 'تقييمات المتاجر'

    def __str__(self):
        return f"{self.store.name} - {self.rating}/5"


class ProductRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_ratings'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-updated_at']
        verbose_name = 'تقييم منتج'
        verbose_name_plural = 'تقييمات المنتجات'

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"
