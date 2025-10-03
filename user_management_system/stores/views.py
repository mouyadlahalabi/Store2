from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.shortcuts import render, redirect
from .models import Category
from .forms import CategoryForm , ProductForm


# صفحة الواجهة الرئيسية للمتجر
def store_front(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "stores/store_front.html", {
        "products": products,
        "categories": categories
    })


# صفحة تفاصيل القسم (يعرض منتجات القسم)
# views.py


def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category
            product.save()
            return redirect("stores:category_detail", id=category.id)  # 👈 مهم: Redirect بعد الحفظ
    else:
        form = ProductForm()

    return render(request, "stores/category_detail.html", {
        "category": category,
        "products": products,
        "form": form,
    })



# صفحة تفاصيل المنتج
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "stores/product_detail.html", {
        "product": product
    })



def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stores:store_front')  # بعد الإضافة ارجع للواجهة الرئيسية
    else:
        form = CategoryForm()
    
    return render(request, "stores/add_category.html", {
        "form": form
    })
from django.shortcuts import redirect, get_object_or_404
from .models import Category

def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('stores:store_front')  # إعادة التوجيه بعد الحذف



def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("stores:product_detail", id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "stores/product_form.html", {"form": form, "product": product})

def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.delete()
        return redirect("stores:category_detail", id=product.category.id)
    return render(request, "stores/product_confirm_delete.html", {"product": product})
