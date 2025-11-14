from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import models
from .models import Product, Category, Store, Sale, Cart, CartItem, FavoriteStore
from .forms import CategoryForm, ProductForm, StoreCreationForm
from .models import FavoriteStore








@login_required
def create_store(request):
    """إنشاء متجر جديد مرتبط بالمستخدم"""
    if not request.user.is_store_owner():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    if request.method == 'POST':
        form = StoreCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # تحقق إن لم يكن للمستخدم متجر بنفس الاسم
            existing_store = Store.objects.filter(owner=request.user, name=form.cleaned_data['name']).exists()
            if existing_store:
                messages.warning(request, 'لديك متجر بنفس الاسم بالفعل!')
                return redirect('stores:store_list_user')

            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(request, 'تم إرسال طلب إنشاء المتجر بنجاح! سيتم مراجعته من قبل الإدارة.')
            return redirect('stores:store_list_user')
    else:
        form = StoreCreationForm()

    return render(request, 'stores/create_store.html', {'form': form})





@login_required
def store_list_user(request):
    """عرض جميع المتاجر الخاصة بالمستخدم الحالي"""
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'stores/store_list_user.html', {'stores': stores})

@login_required
def store_detail(request, store_id):
    """عرض تفاصيل متجر معين"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    return render(request, 'stores/store_detail.html', {'store': store})



@login_required
def edit_store(request, store_id):
    """تعديل متجر"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        form = StoreCreationForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المتجر بنجاح.')
            return redirect('stores:store_detail', store_id=store.id)
    else:
        form = StoreCreationForm(instance=store)

    return render(request, 'stores/edit_store.html', {'form': form, 'store': store})




@login_required
def store_delete(request, store_id):
    """حذف متجر"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        store.delete()
        messages.success(request, 'تم حذف المتجر بنجاح.')
        return redirect('stores:store_list_user')

    messages.error(request, 'لا يمكن حذف المتجر عبر الرابط مباشرة.')
    return redirect('stores:store_list_user')




@login_required
def manage_stores(request):
    """إدارة المتاجر (للمديرين فقط)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    stores = Store.objects.all().order_by('-created_at')
    return render(request, 'stores/manage_stores.html', {'stores': stores})




@login_required
def verify_store(request, store_id):
    """التحقق من المتجر (للمديرين فقط)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    store = get_object_or_404(Store, id=store_id)
    store.is_verified = not store.is_verified
    store.save()

    status = 'تم التحقق من' if store.is_verified else 'تم إلغاء التحقق من'
    messages.success(request, f'{status} المتجر {store.name}.')

    return redirect('stores:manage_stores')



@login_required
def store_requests(request):
    """عرض طلبات المتاجر المعلقة"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    pending_stores = Store.objects.filter(approval_status='pending').order_by('-created_at')
    approved_stores = Store.objects.filter(approval_status='approved').order_by('-approval_date')
    rejected_stores = Store.objects.filter(approval_status='rejected').order_by('-updated_at')

    context = {
        'pending_stores': pending_stores,
        'approved_stores': approved_stores,
        'rejected_stores': rejected_stores,
        'pending_count': pending_stores.count(),
        'approved_count': approved_stores.count(),
        'rejected_count': rejected_stores.count(),
    }

    return render(request, 'stores/store_requests.html', context)


@login_required
def approve_store(request, store_id):
    """الموافقة على متجر"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        store.approval_status = 'approved'
        store.is_verified = True
        store.approved_by = request.user
        store.approval_date = timezone.now()
        store.rejection_reason = ''
        store.save()

        messages.success(request, f'تمت الموافقة على متجر "{store.name}" بنجاح!')
        return redirect('stores:store_requests')

    return render(request, 'stores/approve_store.html', {'store': store})


@login_required
def reject_store(request, store_id):
    """رفض متجر"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')

        if not rejection_reason.strip():
            messages.error(request, 'يجب إدخال سبب الرفض.')
            return render(request, 'stores/reject_store.html', {'store': store})

        store.approval_status = 'rejected'
        store.is_verified = False
        store.approved_by = request.user
        store.approval_date = timezone.now()
        store.rejection_reason = rejection_reason
        store.save()

        messages.success(request, f'تم رفض متجر "{store.name}".')
        return redirect('stores:store_requests')

    return render(request, 'stores/reject_store.html', {'store': store})


@login_required
def store_detail_admin(request, store_id):
    """عرض تفاصيل المتجر للمديرين"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    store = get_object_or_404(Store, id=store_id)

    context = {
        'store': store,
        'can_approve': store.approval_status == 'pending',
        'can_reject': store.approval_status == 'pending',
    }

    return render(request, 'stores/store_detail_admin.html', context)


def store_list(request):
    """عرض جميع المتاجر العامة"""
    stores = Store.objects.filter(is_verified=True)
    return render(request, 'stores/store_list_user.html', {'stores': stores})







# 🔹 صفحة عرض كل المتاجر (عامة)
def store_list(request):
    stores = Store.objects.filter(approval_status='approved')
    return render(request, "stores/store_list.html", {"stores": stores})


# 🔹 صفحة واجهة المتجر الخاصة بالمستخدم الحالي
@login_required
def my_store_front(request):
    store = get_object_or_404(Store, owner=request.user, approval_status='approved')
    products = Product.objects.filter(store=store)
    categories = Category.objects.filter(store=store)

    # تحديد الدور الحالي للمستخدم
    if request.user.is_superuser:
        user_role = "admin"
    elif store.owner == request.user:
        user_role = "owner"
    else:
        user_role = "customer"

    return render(request, "stores/store_front.html", {
        "store": store,
        "products": products,
        "categories": categories,
        "user_role": user_role,
    })

def store_categories(request, store_id):
    """عرض الأقسام الخاصة بمتجر معين"""
    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    categories = Category.objects.filter(store=store)
    return render(request, 'stores/store_categories.html', {
        'store': store,
        'categories': categories,
    })

# 🔹 صفحة واجهة متجر عام حسب الـ ID (مثلاً للمستخدمين الآخرين)
def store_front(request, store_id):
    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    categories = Category.objects.filter(store=store)
    
    # فلتر حسب القسم
    category_filter = request.GET.get('category')
    if category_filter:
        categories = categories.filter(id=category_filter)
    
    # التحقق إذا كان المتجر في المفضلة
    is_favorite = False
    if request.user.is_authenticated and not request.user.is_store_owner():
        is_favorite = FavoriteStore.objects.filter(user=request.user, store=store).exists()

    return render(request, "stores/store_front.html", {
        "store": store,
        "categories": categories,
        "all_categories": Category.objects.filter(store=store).order_by('name'),
        "selected_category": int(category_filter) if category_filter else None,
        "is_favorite": is_favorite,
    })


# 🔹 صفحة تفاصيل القسم في متجر معين
def category_detail(request, store_id, category_id):
    store = get_object_or_404(Store, id=store_id)
    category = get_object_or_404(Category, id=category_id, store=store)
    products = Product.objects.filter(category=category, store=store)

    # ✅ السماح فقط لصاحب المتجر أو المشرف بإضافة منتج
    can_add_product = request.user == store.owner or request.user.is_superuser

    if request.method == "POST":
        if not can_add_product:
            return HttpResponseForbidden("غير مسموح لك بإضافة منتجات في هذا المتجر.")

        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category
            product.store = store
            product.save()
            return redirect("stores:category_detail", store_id=store.id, category_id=category.id)

    else:
        form = ProductForm() if can_add_product else None
        
        # 🔹 تطبيق الفلاتر
        # فلتر حسب السعر
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # فلتر حسب المقاس
        size_filter = request.GET.get('size')
        if size_filter:
            products = products.filter(sizes__icontains=size_filter)
        
        # فلتر حسب التوفر
        in_stock = request.GET.get('in_stock')
        if in_stock == 'true':
            products = products.filter(stock__gt=0)
        elif in_stock == 'false':
            products = products.filter(stock=0)
        
        # ترتيب المنتجات
        sort_by = request.GET.get('sort', 'created_at')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'stock':
            products = products.order_by('-stock')
        else:
            products = products.order_by('-created_at')
        
        # جلب جميع المقاسات المتاحة
        all_sizes = set()
        for product in Product.objects.filter(category=category, store=store):
            if product.sizes:
                sizes_list = [s.strip() for s in product.sizes.split(',')]
                all_sizes.update(sizes_list)
        all_sizes = sorted(list(all_sizes))
        
        # حساب نطاق الأسعار
        price_range = products.aggregate(
            min_price=models.Min('price'),
            max_price=models.Max('price')
        )

    return render(request, "stores/category_detail.html", {
        "store": store,
        "category": category,
        "products": products,
        "form": form,
        "can_add_product": can_add_product,
        "all_sizes": all_sizes,
        "price_range": price_range,
        "current_filters": {
            "min_price": min_price or "",
            "max_price": max_price or "",
            "size": size_filter or "",
            "in_stock": in_stock or "",
            "sort": sort_by,
        }
    })
@login_required
def add_to_cart(request, store_id, product_id):
    product = get_object_or_404(Product, id=product_id, store_id=store_id)

    # احصل على السلة الخاصة بالمستخدم أو أنشئ واحدة
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)

    # تحقق إذا المنتج موجود بالفعل في السلة
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()

    messages.success(request, f'تم إضافة {product.name} إلى السلة بنجاح.')
    return redirect('stores:cart_detail')


@login_required
def add_product(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('stores:store_front', store_id=store.id)
    else:
        form = ProductForm()

    return render(request, "stores/add_product.html", {
        "store": store,
        "form": form
    })
    


# 🔹 صفحة تفاصيل المنتج
def product_detail(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id)
    product = get_object_or_404(Product, id=product_id, store=store)
    return render(request, "stores/product_detail.html", {
        "store": store,
        "product": product
    })


# 🔹 إضافة قسم جديد لمتجر معين
@login_required
def add_category(request, store_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.store = store
            category.save()
            return redirect('stores:store_front', store_id=store.id)
    else:
        form = CategoryForm()
    
    return render(request, "stores/add_category.html", {
        "store": store,
        "form": form
    })

from django.contrib import messages
# 🔹 حذف قسم من متجر معين
@login_required
def delete_category(request, store_id, category_id):
    # اجلب المتجر بدون شرط المالك
    store = get_object_or_404(Store, id=store_id)

    # اسمح فقط لصاحب المتجر أو المدير
    if store.owner != request.user and not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بحذف هذا التصنيف.')

    category = get_object_or_404(Category, id=category_id, store=store)
    category.delete()
    messages.success(request, 'تم حذف التصنيف بنجاح.')
    return redirect('stores:store_categories', store_id=store.id)



# 🔹 تعديل منتج في متجر معين
@login_required
def product_edit(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("stores:product_detail", store_id=store.id, product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "stores/product_form.html", {"form": form, "store": store, "product": product})


# 🔹 حذف منتج من متجر معين
@login_required
def product_delete(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        # حفظ category_id قبل حذف المنتج
        category_id = product.category.id
        product.delete()
        messages.success(request, 'تم حذف المنتج بنجاح.')
        return redirect("stores:category_detail", store_id=store.id, category_id=category_id)
    return render(request, "stores/product_confirm_delete.html", {"store": store, "product": product})

@login_required
def store_sales(request):
    # تأكد أن المستخدم صاحب متجر
    store = get_object_or_404(Store, owner=request.user)

    # جميع المبيعات الخاصة بالمتجر (فقط للمنتجات الموجودة)
    sales = Sale.objects.filter(store=store, product__isnull=False).select_related('product', 'buyer').order_by('-created_at')

    return render(request, 'stores/store_sales.html', {
        'store': store,
        'sales': sales
    })


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    return render(request, 'stores/cart_detail.html', {'cart': cart})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('stores:cart_detail')


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect('stores:cart_detail')


# 🔹 إضافة/حذف متجر من المفضلة
@login_required
def toggle_favorite_store(request, store_id):
    """إضافة أو حذف متجر من قائمة المفضلة"""
    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    
    # التحقق إذا كان المتجر موجود في المفضلة
    favorite, created = FavoriteStore.objects.get_or_create(
        user=request.user,
        store=store
    )
    
    if not created:
        # إذا كان موجود، احذفه
        favorite.delete()
        messages.success(request, f'تم إزالة {store.name} من المفضلة.')
        is_favorite = False
    else:
        # إذا لم يكن موجود، أضفه
        messages.success(request, f'تم إضافة {store.name} إلى المفضلة.')
        is_favorite = True
    
    # إرجاع JSON response للاستخدام مع AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'is_favorite': is_favorite})
    
    # إرجاع redirect للاستخدام العادي
    return redirect(request.META.get('HTTP_REFERER', 'stores:favorite_stores'))


# 🔹 صفحة المتاجر المفضلة
@login_required
def favorite_stores(request):
    """عرض قائمة المتاجر المفضلة للمستخدم"""
    favorite_stores_list = FavoriteStore.objects.filter(
        user=request.user
    ).select_related('store').order_by('-created_at')
    
    stores = [fav.store for fav in favorite_stores_list]
    
    return render(request, 'stores/favorite_stores.html', {
        'favorite_stores': stores,
        'favorite_count': len(stores)
    })
