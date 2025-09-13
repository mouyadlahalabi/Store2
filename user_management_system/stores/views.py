from django.shortcuts import render, get_object_or_404
from .models import Product, Category

# صفحة الواجهة الرئيسية للمتجر
def store_front(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "stores/store_front.html", {
        "products": products,
        "categories": categories
    })


# صفحة تفاصيل القسم (يعرض منتجات القسم)
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    return render(request, "stores/category_detail.html", {
        "category": category,
        "products": products
    })

# صفحة تفاصيل المنتج
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "stores/product_detail.html", {
        "product": product
    })
