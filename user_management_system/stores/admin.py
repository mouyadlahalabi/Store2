from django.contrib import admin
from .models import Product, Category, ProductSizeStock

admin.site.register(Category)

class ProductSizeStockInline(admin.TabularInline):
    model = ProductSizeStock
    extra = 1
    fields = ('size', 'stock')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeStockInline]
    list_display = ('name', 'store', 'category', 'price', 'get_total_stock_display')
    
    def get_total_stock_display(self, obj):
        return obj.get_total_stock()
    get_total_stock_display.short_description = 'إجمالي الكمية'
