from django.contrib import admin
from .models import (
    Product,
    Category,
    ProductSizeStock,
    FavoriteProduct,
    StoreRating,
    ProductRating,
)


admin.site.register(Category)


class ProductSizeStockInline(admin.TabularInline):
    model = ProductSizeStock
    extra = 1
    fields = ('size', 'stock')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeStockInline]
    list_display = (
        'name',
        'store',
        'category',
        'price',
        'original_price',
        'get_total_stock_display',
        'is_on_offer',
    )

    def get_total_stock_display(self, obj):
        return obj.get_total_stock()

    get_total_stock_display.short_description = 'إجمالي الكمية'


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')


@admin.register(StoreRating)
class StoreRatingAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'rating', 'updated_at')
    list_filter = ('rating',)
    search_fields = ('store__name', 'user__username')


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'updated_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'user__username')
