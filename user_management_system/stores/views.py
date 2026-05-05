from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.db import models
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth
from .models import (
    Product,
    Category,
    Store,
    Sale,
    Cart,
    CartItem,
    FavoriteProduct,
    ProductSizeStock,
    StoreRating,
    ProductRating,
)
from .forms import (
    CategoryForm,
    ProductForm,
    StoreCreationForm,
    StoreRatingForm,
    ProductRatingForm,
)








@login_required
def create_store(request):
    """ط¥ظ†ط´ط§ط، ظ…طھط¬ط± ط¬ط¯ظٹط¯ ظ…ط±طھط¨ط· ط¨ط§ظ„ظ…ط³طھط®ط¯ظ…"""
    if not request.user.is_store_owner():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    if request.method == 'POST':
        form = StoreCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # طھط­ظ‚ظ‚ ط¥ظ† ظ„ظ… ظٹظƒظ† ظ„ظ„ظ…ط³طھط®ط¯ظ… ظ…طھط¬ط± ط¨ظ†ظپط³ ط§ظ„ط§ط³ظ…
            existing_store = Store.objects.filter(owner=request.user, name=form.cleaned_data['name']).exists()
            if existing_store:
                messages.warning(request, 'ظ„ط¯ظٹظƒ ظ…طھط¬ط± ط¨ظ†ظپط³ ط§ظ„ط§ط³ظ… ط¨ط§ظ„ظپط¹ظ„!')
                return redirect('stores:store_list_user')

            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(request, 'طھظ… ط¥ط±ط³ط§ظ„ ط·ظ„ط¨ ط¥ظ†ط´ط§ط، ط§ظ„ظ…طھط¬ط± ط¨ظ†ط¬ط§ط­! ط³ظٹطھظ… ظ…ط±ط§ط¬ط¹طھظ‡ ظ…ظ† ظ‚ط¨ظ„ ط§ظ„ط¥ط¯ط§ط±ط©.')
            return redirect('stores:store_list_user')
    else:
        form = StoreCreationForm()

    return render(request, 'stores/create_store.html', {'form': form})





@login_required
def store_list_user(request):
    """ط¹ط±ط¶ ط¬ظ…ظٹط¹ ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ط®ط§طµط© ط¨ط§ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط­ط§ظ„ظٹ"""
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'stores/store_list_user.html', {'stores': stores})

@login_required
def store_detail(request, store_id):
    """ط¹ط±ط¶ طھظپط§طµظٹظ„ ظ…طھط¬ط± ظ…ط¹ظٹظ†"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    return render(request, 'stores/store_detail.html', {'store': store})



@login_required
def edit_store(request, store_id):
    """طھط¹ط¯ظٹظ„ ظ…طھط¬ط±"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        form = StoreCreationForm(request.POST, request.FILES, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'طھظ… طھط­ط¯ظٹط« ط§ظ„ظ…طھط¬ط± ط¨ظ†ط¬ط§ط­.')
            return redirect('stores:store_detail', store_id=store.id)
    else:
        form = StoreCreationForm(instance=store)

    return render(request, 'stores/edit_store.html', {'form': form, 'store': store})




@login_required
def store_delete(request, store_id):
    """ط­ط°ظپ ظ…طھط¬ط±"""
    store = get_object_or_404(Store, id=store_id, owner=request.user)

    if request.method == 'POST':
        store.delete()
        messages.success(request, 'طھظ… ط­ط°ظپ ط§ظ„ظ…طھط¬ط± ط¨ظ†ط¬ط§ط­.')
        return redirect('stores:store_list_user')

    messages.error(request, 'ظ„ط§ ظٹظ…ظƒظ† ط­ط°ظپ ط§ظ„ظ…طھط¬ط± ط¹ط¨ط± ط§ظ„ط±ط§ط¨ط· ظ…ط¨ط§ط´ط±ط©.')
    return redirect('stores:store_list_user')




@login_required
def manage_stores(request):
    """ط¥ط¯ط§ط±ط© ط§ظ„ظ…طھط§ط¬ط± (ظ„ظ„ظ…ط¯ظٹط±ظٹظ† ظپظ‚ط·)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    stores = Store.objects.all().order_by('-created_at')
    return render(request, 'stores/manage_stores.html', {'stores': stores})




@login_required
def verify_store(request, store_id):
    """ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظ…طھط¬ط± (ظ„ظ„ظ…ط¯ظٹط±ظٹظ† ظپظ‚ط·)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    store = get_object_or_404(Store, id=store_id)
    store.is_verified = not store.is_verified
    store.save()

    status = 'طھظ… ط§ظ„طھط­ظ‚ظ‚ ظ…ظ†' if store.is_verified else 'طھظ… ط¥ظ„ط؛ط§ط، ط§ظ„طھط­ظ‚ظ‚ ظ…ظ†'
    messages.success(request, f'{status} ط§ظ„ظ…طھط¬ط± {store.name}.')

    return redirect('stores:manage_stores')



@login_required
def store_requests(request):
    """ط¹ط±ط¶ ط·ظ„ط¨ط§طھ ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ظ…ط¹ظ„ظ‚ط©"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

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
    """ط§ظ„ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…طھط¬ط±"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        store.approval_status = 'approved'
        store.is_verified = True
        store.approved_by = request.user
        store.approval_date = timezone.now()
        store.rejection_reason = ''
        store.save()

        messages.success(request, f'طھظ…طھ ط§ظ„ظ…ظˆط§ظپظ‚ط© ط¹ظ„ظ‰ ظ…طھط¬ط± "{store.name}" ط¨ظ†ط¬ط§ط­!')
        return redirect('stores:store_requests')

    return render(request, 'stores/approve_store.html', {'store': store})


@login_required
def reject_store(request, store_id):
    """ط±ظپط¶ ظ…طھط¬ط±"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')

        if not rejection_reason.strip():
            messages.error(request, 'ظٹط¬ط¨ ط¥ط¯ط®ط§ظ„ ط³ط¨ط¨ ط§ظ„ط±ظپط¶.')
            return render(request, 'stores/reject_store.html', {'store': store})

        store.approval_status = 'rejected'
        store.is_verified = False
        store.approved_by = request.user
        store.approval_date = timezone.now()
        store.rejection_reason = rejection_reason
        store.save()

        messages.success(request, f'طھظ… ط±ظپط¶ ظ…طھط¬ط± "{store.name}".')
        return redirect('stores:store_requests')

    return render(request, 'stores/reject_store.html', {'store': store})


@login_required
def store_detail_admin(request, store_id):
    """ط¹ط±ط¶ طھظپط§طµظٹظ„ ط§ظ„ظ…طھط¬ط± ظ„ظ„ظ…ط¯ظٹط±ظٹظ†"""
    if not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط§ظ„ظˆطµظˆظ„ ط¥ظ„ظ‰ ظ‡ط°ظ‡ ط§ظ„طµظپط­ط©.')

    store = get_object_or_404(Store, id=store_id)

    context = {
        'store': store,
        'can_approve': store.approval_status == 'pending',
        'can_reject': store.approval_status == 'pending',
    }

    return render(request, 'stores/store_detail_admin.html', context)


def store_list(request):
    """ط¹ط±ط¶ ط¬ظ…ظٹط¹ ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ط¹ط§ظ…ط©"""
    stores = Store.objects.filter(approval_status='approved', is_active=True)
    return render(request, 'stores/store_list.html', {'stores': stores})







# store_list ظ…ط¹ط±ظ‘ظپ ط£ط¹ظ„ط§ظ‡ - ظٹط¹ط±ط¶ ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ظ…ط¹طھظ…ط¯ط©


# ًں”¹ طµظپط­ط© ظˆط§ط¬ظ‡ط© ط§ظ„ظ…طھط¬ط± ط§ظ„ط®ط§طµط© ط¨ط§ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط­ط§ظ„ظٹ
@login_required
def my_store_front(request):
    store = get_object_or_404(Store, owner=request.user, approval_status='approved')
    products = Product.objects.filter(store=store)
    categories = Category.objects.filter(store=store)

    # طھط­ط¯ظٹط¯ ط§ظ„ط¯ظˆط± ط§ظ„ط­ط§ظ„ظٹ ظ„ظ„ظ…ط³طھط®ط¯ظ…
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
    """ط¹ط±ط¶ ط§ظ„ط£ظ‚ط³ط§ظ… ط§ظ„ط®ط§طµط© ط¨ظ…طھط¬ط± ظ…ط¹ظٹظ†"""
    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    categories = Category.objects.filter(store=store)
    return render(request, 'stores/store_categories.html', {
        'store': store,
        'categories': categories,
    })


def categories_all(request):
    """ط¹ط±ط¶ ط¬ظ…ظٹط¹ ط§ظ„ظپط¦ط§طھ ظ…ظ† ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ظ…ط¹طھظ…ط¯ط©"""
    categories = Category.objects.filter(
        store__approval_status='approved',
        store__is_active=True
    ).values('name').annotate(
        product_count=Count('products')
    ).order_by('-product_count')
    return render(request, 'stores/categories_all.html', {'categories': categories})


def category_products_by_name(request, category_name):
    """ط¹ط±ط¶ ط§ظ„ظ…ظ†طھط¬ط§طھ ط­ط³ط¨ ط§ط³ظ… ط§ظ„ظپط¦ط© ظ…ظ† ط¬ظ…ظٹط¹ ط§ظ„ظ…طھط§ط¬ط±"""
    products = Product.objects.filter(
        category__name=category_name,
        category__store__approval_status='approved',
        category__store__is_active=True
    ).select_related('store', 'category').order_by('-created_at')
    favorite_product_ids = set()
    if request.user.is_authenticated:
        favorite_product_ids = set(
            FavoriteProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    return render(request, 'stores/category_products.html', {
        'products': products,
        'category_name': category_name,
        'favorite_product_ids': favorite_product_ids,
    })


def offers_list(request):
    """ط¹ط±ط¶ ط§ظ„ط¹ط±ظˆط¶ - ط§ظ„ظ…ظ†طھط¬ط§طھ ط°ط§طھ ط§ظ„ط®طµظ… ظ…ظ† ط§ظ„ظ…طھط§ط¬ط± ط§ظ„ظ…ط¹طھظ…ط¯ط©"""
    products = Product.objects.filter(
        store__approval_status='approved',
        store__is_active=True,
        original_price__isnull=False,
        original_price__gt=models.F('price')
    ).select_related('store', 'category').order_by('-created_at')[:48]
    favorite_product_ids = set()
    if request.user.is_authenticated:
        favorite_product_ids = set(
            FavoriteProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    return render(request, 'stores/offers_list.html', {
        'products': products,
        'favorite_product_ids': favorite_product_ids,
    })

# ًں”¹ طµظپط­ط© ظˆط§ط¬ظ‡ط© ظ…طھط¬ط± ط¹ط§ظ… ط­ط³ط¨ ط§ظ„ظ€ ID (ظ…ط«ظ„ط§ظ‹ ظ„ظ„ظ…ط³طھط®ط¯ظ…ظٹظ† ط§ظ„ط¢ط®ط±ظٹظ†)
def store_front(request, store_id):
    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    categories = Category.objects.filter(store=store)
    
    # ظپظ„طھط± ط­ط³ط¨ ط§ظ„ظ‚ط³ظ…
    category_filter = request.GET.get('category')
    if category_filter:
        categories = categories.filter(id=category_filter)
    
    # ظ…ظ†طھط¬ط§طھ ط§ظ„ط¹ط±ظˆط¶ (ظ„طµط§ط­ط¨ ط§ظ„ظ…طھط¬ط± ظˆط§ظ„ط²ظˆط§ط±)
    offer_products = Product.objects.filter(
        store=store,
        original_price__isnull=False,
        original_price__gt=models.F('price')
    ).select_related('category')

    favorite_product_ids = set()
    if request.user.is_authenticated:
        favorite_product_ids = set(
            FavoriteProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    user_store_rating = None
    store_rating_form = None
    if request.user.is_authenticated and not request.user.is_store_owner():
        user_store_rating = StoreRating.objects.filter(user=request.user, store=store).first()
        store_rating_form = StoreRatingForm(instance=user_store_rating)

    return render(request, "stores/store_front.html", {
        "store": store,
        "categories": categories,
        "all_categories": Category.objects.filter(store=store).order_by('name'),
        "selected_category": int(category_filter) if category_filter else None,
        "offer_products": offer_products,
        "favorite_product_ids": favorite_product_ids,
        "store_ratings": store.ratings.select_related('user')[:8],
        "user_store_rating": user_store_rating,
        "store_rating_form": store_rating_form,
    })


# ًں”¹ طµظپط­ط© طھظپط§طµظٹظ„ ط§ظ„ظ‚ط³ظ… ظپظٹ ظ…طھط¬ط± ظ…ط¹ظٹظ†
def category_detail(request, store_id, category_id):
    store = get_object_or_404(Store, id=store_id)
    category = get_object_or_404(Category, id=category_id, store=store)
    products = Product.objects.filter(category=category, store=store)

    # âœ… ط§ظ„ط³ظ…ط§ط­ ظپظ‚ط· ظ„طµط§ط­ط¨ ط§ظ„ظ…طھط¬ط± ط£ظˆ ط§ظ„ظ…ط´ط±ظپ ط¨ط¥ط¶ط§ظپط© ظ…ظ†طھط¬
    can_add_product = request.user == store.owner or request.user.is_superuser

    if request.method == "POST":
        if not can_add_product:
            return HttpResponseForbidden("ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط¥ط¶ط§ظپط© ظ…ظ†طھط¬ط§طھ ظپظٹ ظ‡ط°ط§ ط§ظ„ظ…طھط¬ط±.")

        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category
            product.store = store
            product.save()
            messages.success(request, f'طھظ… ط¥ط¶ط§ظپط© ط§ظ„ظ…ظ†طھط¬ "{product.name}" ط¨ظ†ط¬ط§ط­.')
            return redirect("stores:category_detail", store_id=store.id, category_id=category.id)

    else:
        form = ProductForm() if can_add_product else None
        
        # ًں”¹ طھط·ط¨ظٹظ‚ ط§ظ„ظپظ„ط§طھط±
        # ظپظ„طھط± ط­ط³ط¨ ط§ظ„ط³ط¹ط±
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
        
        # ظپظ„طھط± ط­ط³ط¨ ط§ظ„ظ…ظ‚ط§ط³
        size_filter = request.GET.get('size')
        if size_filter:
            products = products.filter(sizes__icontains=size_filter)
        
        # ظپظ„طھط± ط­ط³ط¨ ط§ظ„طھظˆظپط±
        in_stock = request.GET.get('in_stock')
        if in_stock == 'true':
            products = products.filter(stock__gt=0)
        elif in_stock == 'false':
            products = products.filter(stock=0)
        
        # طھط±طھظٹط¨ ط§ظ„ظ…ظ†طھط¬ط§طھ
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
        
        # ط¬ظ„ط¨ ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ‚ط§ط³ط§طھ ط§ظ„ظ…طھط§ط­ط©
        all_sizes = set()
        for product in Product.objects.filter(category=category, store=store):
            if product.sizes:
                sizes_list = [s.strip() for s in product.sizes.split(',')]
                all_sizes.update(sizes_list)
        all_sizes = sorted(list(all_sizes))
        
        # ط­ط³ط§ط¨ ظ†ط·ط§ظ‚ ط§ظ„ط£ط³ط¹ط§ط±
        price_range = products.aggregate(
            min_price=models.Min('price'),
            max_price=models.Max('price')
        )

    favorite_product_ids = set()
    if request.user.is_authenticated:
        favorite_product_ids = set(
            FavoriteProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
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
        },
        "favorite_product_ids": favorite_product_ids,
    })
@login_required
def purchase_product(request, store_id, product_id):
    """طµظپط­ط© طھط­ط¯ظٹط¯ ط§ظ„ظƒظ…ظٹط© ظˆط§ظ„ظ…ظ‚ط§ط³ ظ‚ط¨ظ„ ط¥ط¶ط§ظپط© ط§ظ„ظ…ظ†طھط¬ ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط©"""
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'ط§ظ„ط³ظ„ط© ظ…طھط§ط­ط© ظ„ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط¹ط§ط¯ظٹ ظپظ‚ط·.')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id, store_id=store_id, store__approval_status='approved')
    store = product.store
    
    # ط¬ظ„ط¨ ط§ظ„ظƒظ…ظٹط§طھ ط­ط³ط¨ ط§ظ„ظ…ظ‚ط§ط³
    size_stocks = {}
    for size_stock in product.size_stocks.all():
        size_stocks[size_stock.size] = size_stock.stock
    
    # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† طھظˆظپط± ط§ظ„ظ…ظ†طھط¬
    total_stock = product.get_total_stock()
    if total_stock <= 0:
        messages.error(request, 'ط¹ط°ط±ط§ظ‹طŒ ظ‡ط°ط§ ط§ظ„ظ…ظ†طھط¬ ط؛ظٹط± ظ…طھظˆظپط± ط­ط§ظ„ظٹط§ظ‹.')
        return redirect('stores:category_detail', store_id=store_id, category_id=product.category.id)
    
    if request.method == 'POST':
        # ط¬ظ„ط¨ ط§ظ„ط¨ظٹط§ظ†ط§طھ ظ…ظ† ط§ظ„ظ†ظ…ظˆط°ط¬
        size_quantities = {}  # {size: quantity}
        
        # ط¬ظ…ط¹ ط§ظ„ظƒظ…ظٹط§طھ ظ…ظ† ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ‚ط§ط³ط§طھ
        for size in size_stocks.keys():
            qty = request.POST.get(f'quantity_{size}', '0')
            try:
                qty = int(qty)
                if qty > 0:
                    size_quantities[size] = qty
            except ValueError:
                pass
        
        # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ظˆط¬ظˆط¯ ظƒظ…ظٹط§طھ ظ…ط­ط¯ط¯ط©
        if not size_quantities:
            messages.error(request, 'ظٹط±ط¬ظ‰ طھط­ط¯ظٹط¯ ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…ط·ظ„ظˆط¨ط© ط¹ظ„ظ‰ ط§ظ„ط£ظ‚ظ„ ظ„ظ…ظ‚ط§ط³ ظˆط§ط­ط¯.')
            return render(request, 'stores/purchase_product.html', {
                'product': product,
                'store': store,
                'size_stocks': size_stocks,
            })
        
        # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط§طھ ط§ظ„ظ…طھط§ط­ط© ظ„ظƒظ„ ظ…ظ‚ط§ط³
        errors = []
        for size, requested_qty in size_quantities.items():
            available_qty = size_stocks.get(size, 0)
            
            # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ظپظٹ ط§ظ„ط³ظ„ط© ط§ظ„ط­ط§ظ„ظٹط©
            cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
            existing_item = CartItem.objects.filter(cart=cart, product=product, size=size).first()
            if existing_item:
                available_qty -= existing_item.quantity
            
            if requested_qty > available_qty:
                errors.append(f'ط§ظ„ظ…ظ‚ط§ط³ {size}: ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ‡ظٹ {available_qty} ظ‚ط·ط¹ط© ظپظ‚ط·.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'stores/purchase_product.html', {
                'product': product,
                'store': store,
                'size_stocks': size_stocks,
            })
        
        # ط¥ط¶ط§ظپط© ط§ظ„ظ…ظ†طھط¬ط§طھ ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط©
        cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
        added_items = []
        
        for size, quantity in size_quantities.items():
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                # ط¥ط°ط§ ظƒط§ظ† ط§ظ„ظ…ظ†طھط¬ ظ…ظˆط¬ظˆط¯ ظپظٹ ط§ظ„ط³ظ„ط© ط¨ظ†ظپط³ ط§ظ„ظ…ظ‚ط§ط³طŒ ط£ط¶ظپ ط§ظ„ظƒظ…ظٹط©
                cart_item.quantity += quantity
                cart_item.save()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            
            added_items.append(f"{quantity} ظ‚ط·ط¹ط© ظ…ظ† {size}")
        
        messages.success(request, f'طھظ… ط¥ط¶ط§ظپط© {", ".join(added_items)} ظ…ظ† {product.name} ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط© ط¨ظ†ط¬ط§ط­.')
        return redirect('stores:cart_detail')
    
    return render(request, 'stores/purchase_product.html', {
        'product': product,
        'store': store,
        'size_stocks': size_stocks,
    })


@login_required
def add_to_cart(request, store_id, product_id):
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'السلة متاحة للمستخدم العادي فقط.')
        return redirect('home')


    """ط¥ط¶ط§ظپط© ظ…ظ†طھط¬ ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط© ظ…ط¹ ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط©"""
    product = get_object_or_404(Product, id=product_id, store_id=store_id)

    # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† طھظˆظپط± ط§ظ„ظ…ظ†طھط¬
    if product.stock <= 0:
        messages.error(request, 'ط¹ط°ط±ط§ظ‹طŒ ظ‡ط°ط§ ط§ظ„ظ…ظ†طھط¬ ط؛ظٹط± ظ…طھظˆظپط± ط­ط§ظ„ظٹط§ظ‹.')
        return redirect('stores:category_detail', store_id=store_id, category_id=product.category.id)

    # ط§ط­طµظ„ ط¹ظ„ظ‰ ط§ظ„ط³ظ„ط© ط§ظ„ط®ط§طµط© ط¨ط§ظ„ظ…ط³طھط®ط¯ظ… ط£ظˆ ط£ظ†ط´ط¦ ظˆط§ط­ط¯ط©
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)

    # طھط­ظ‚ظ‚ ط¥ط°ط§ ط§ظ„ظ…ظ†طھط¬ ظ…ظˆط¬ظˆط¯ ط¨ط§ظ„ظپط¹ظ„ ظپظٹ ط§ظ„ط³ظ„ط©
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        # ط¥ط°ط§ ظƒط§ظ† ط§ظ„ظ…ظ†طھط¬ ظ…ظˆط¬ظˆط¯طŒ طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط©
        new_quantity = cart_item.quantity + 1
        if new_quantity > product.stock:
            messages.error(request, f'ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ‡ظٹ {product.stock} ظ‚ط·ط¹ط© ظپظ‚ط·. ظ„ط¯ظٹظƒ ط¨ط§ظ„ظپط¹ظ„ {cart_item.quantity} ظ‚ط·ط¹ط© ظپظٹ ط§ظ„ط³ظ„ط©.')
            return redirect('stores:purchase_product', store_id=store_id, product_id=product_id)
        cart_item.quantity = new_quantity
    else:
        cart_item.quantity = 1
    
    cart_item.save()
    messages.success(request, f'طھظ… ط¥ط¶ط§ظپط© {product.name} ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط© ط¨ظ†ط¬ط§ط­.')
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
    


# ًں”¹ طµظپط­ط© طھظپط§طµظٹظ„ ط§ظ„ظ…ظ†طھط¬
def product_detail(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id)
    product = get_object_or_404(Product, id=product_id, store=store)
    is_product_favorite = False
    user_product_rating = None
    user_store_rating = None
    product_rating_form = None
    store_rating_form = None

    if request.user.is_authenticated:
        is_product_favorite = FavoriteProduct.objects.filter(
            user=request.user,
            product=product
        ).exists()

        if not request.user.is_store_owner():
            user_product_rating = ProductRating.objects.filter(user=request.user, product=product).first()
            user_store_rating = StoreRating.objects.filter(user=request.user, store=store).first()
            product_rating_form = ProductRatingForm(instance=user_product_rating)
            store_rating_form = StoreRatingForm(instance=user_store_rating)

    return render(request, "stores/product_detail.html", {
        "store": store,
        "product": product,
        "is_product_favorite": is_product_favorite,
        "product_ratings": product.ratings.select_related('user')[:10],
        "store_ratings": store.ratings.select_related('user')[:8],
        "user_product_rating": user_product_rating,
        "user_store_rating": user_store_rating,
        "product_rating_form": product_rating_form,
        "store_rating_form": store_rating_form,
    })


# ًں”¹ ط¥ط¶ط§ظپط© ظ‚ط³ظ… ط¬ط¯ظٹط¯ ظ„ظ…طھط¬ط± ظ…ط¹ظٹظ†
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
# ًں”¹ ط­ط°ظپ ظ‚ط³ظ… ظ…ظ† ظ…طھط¬ط± ظ…ط¹ظٹظ†
@login_required
def delete_category(request, store_id, category_id):
    # ط§ط¬ظ„ط¨ ط§ظ„ظ…طھط¬ط± ط¨ط¯ظˆظ† ط´ط±ط· ط§ظ„ظ…ط§ظ„ظƒ
    store = get_object_or_404(Store, id=store_id)

    # ط§ط³ظ…ط­ ظپظ‚ط· ظ„طµط§ط­ط¨ ط§ظ„ظ…طھط¬ط± ط£ظˆ ط§ظ„ظ…ط¯ظٹط±
    if store.owner != request.user and not request.user.is_admin():
        return HttpResponseForbidden('ط؛ظٹط± ظ…ط³ظ…ظˆط­ ظ„ظƒ ط¨ط­ط°ظپ ظ‡ط°ط§ ط§ظ„طھطµظ†ظٹظپ.')

    category = get_object_or_404(Category, id=category_id, store=store)
    category.delete()
    messages.success(request, 'طھظ… ط­ط°ظپ ط§ظ„طھطµظ†ظٹظپ ط¨ظ†ط¬ط§ط­.')
    return redirect('stores:store_categories', store_id=store.id)



# ًں”¹ طھط¹ط¯ظٹظ„ ظ…ظ†طھط¬ ظپظٹ ظ…طھط¬ط± ظ…ط¹ظٹظ†
@login_required
def product_edit(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'طھظ… ط­ظپط¸ ط§ظ„ظ…ظ†طھط¬ ط¨ظ†ط¬ط§ط­.')
            return redirect("stores:product_detail", store_id=store.id, product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, "stores/product_form.html", {"form": form, "store": store, "product": product})


# ًں”¹ ط­ط°ظپ ظ…ظ†طھط¬ ظ…ظ† ظ…طھط¬ط± ظ…ط¹ظٹظ†
@login_required
def product_delete(request, store_id, product_id):
    store = get_object_or_404(Store, id=store_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        # ط­ظپط¸ category_id ظ‚ط¨ظ„ ط­ط°ظپ ط§ظ„ظ…ظ†طھط¬
        category_id = product.category.id
        product.delete()
        messages.success(request, 'طھظ… ط­ط°ظپ ط§ظ„ظ…ظ†طھط¬ ط¨ظ†ط¬ط§ط­.')
        return redirect("stores:category_detail", store_id=store.id, category_id=category_id)
    return render(request, "stores/product_confirm_delete.html", {"store": store, "product": product})

@login_required
def store_sales(request):
    """ط³ط¬ظ„ ظƒط§ظ…ظ„ ظ„ط¬ظ…ظٹط¹ ط§ظ„ظ…ط¨ظٹط¹ط§طھ ظ„ظ„ظ…طھط¬ط± - ظ„ظ„ظ‚ط±ط§ط،ط© ظپظ‚ط·"""
    if not request.user.is_store_owner():
        messages.error(request, 'ظˆط§ط¬ظ‡ط© ط§ظ„ظ…ط¨ظٹط¹ط§طھ ظ…طھط§ط­ط© ظ„طµط§ط­ط¨ ط§ظ„ظ…طھط¬ط± ظپظ‚ط·.')
        return redirect('home')

    store = Store.objects.filter(owner=request.user, approval_status='approved').first()
    if not store:
        messages.warning(request, 'ظ„ط§ ظٹظˆط¬ط¯ ظ…طھط¬ط± ظ…ط¹طھظ…ط¯ ظ…ط±طھط¨ط· ط¨ط­ط³ط§ط¨ظƒ ط­طھظ‰ ط§ظ„ط¢ظ†.')
        return redirect('dashboard')

    # ط¬ظ…ظٹط¹ ط§ظ„ظ…ط¨ظٹط¹ط§طھ ط§ظ„ط®ط§طµط© ط¨ط§ظ„ظ…طھط¬ط± (ظپظ‚ط· ظ„ظ„ظ…ظ†طھط¬ط§طھ ط§ظ„ظ…ظˆط¬ظˆط¯ط©)
    sales_query = Sale.objects.filter(store=store, product__isnull=False).select_related('product', 'buyer')
    
    # ظپظ„طھط±ط© ط­ط³ط¨ ط§ظ„طھط§ط±ظٹط® ط¥ط°ط§ طھظ… طھط­ط¯ظٹط¯ظ‡
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        sales_query = sales_query.filter(created_at__gte=date_from)
    if date_to:
        sales_query = sales_query.filter(created_at__lte=date_to)
    
    # طھط±طھظٹط¨ ط­ط³ط¨ ط§ظ„طھط§ط±ظٹط® (ط§ظ„ط£ط­ط¯ط« ط£ظˆظ„ط§ظ‹)
    sales = sales_query.order_by('-created_at')
    
    # ط­ط³ط§ط¨ ط§ظ„ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„ط¥ط¬ظ…ط§ظ„ظٹط©
    total_sales_count = sales.count()
    total_revenue = sum(sale.total_price() for sale in sales)
    average_sale = total_revenue / total_sales_count if total_sales_count > 0 else 0
    
    # ط¥ط­طµط§ط¦ظٹط§طھ ط­ط³ط¨ ط§ظ„ظ…ظ†طھط¬
    product_stats = sales.values('product__name', 'product__id').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price')),
        sale_count=Count('id')
    ).order_by('-total_revenue')[:10]  # ط£ظپط¶ظ„ 10 ظ…ظ†طھط¬ط§طھ
    
    # ط¥ط­طµط§ط¦ظٹط§طھ ط­ط³ط¨ ط§ظ„ط´ظ‡ط±
    monthly_stats = sales.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_revenue=Sum(F('quantity') * F('price')),
        total_count=Count('id')
    ).order_by('-month')[:12]  # ط¢ط®ط± 12 ط´ظ‡ط±
    
    # ط¥ط­طµط§ط¦ظٹط§طھ ط­ط³ط¨ ط§ظ„ظ…ط´طھط±ظٹ
    buyer_stats = sales.values('buyer__username', 'buyer__id').annotate(
        total_purchases=Sum(F('quantity') * F('price')),
        purchase_count=Count('id')
    ).order_by('-total_purchases')[:10]  # ط£ظپط¶ظ„ 10 ظ…ط´طھط±ظٹظ†

    return render(request, 'stores/store_sales.html', {
        'store': store,
        'sales': sales,
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'average_sale': average_sale,
        'product_stats': product_stats,
        'monthly_stats': monthly_stats,
        'buyer_stats': buyer_stats,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def cart_detail(request):
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'السلة متاحة للمستخدم العادي فقط.')
        return redirect('home')


    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    return render(request, 'stores/cart_detail.html', {'cart': cart})


@login_required
def checkout(request):
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'السلة متاحة للمستخدم العادي فقط.')
        return redirect('home')


    """ط¥طھظ…ط§ظ… ط¹ظ…ظ„ظٹط© ط§ظ„ط´ط±ط§ط، ظˆط¥ظ†ط´ط§ط، ط³ط¬ظ„ط§طھ ط§ظ„ظ…ط¨ظٹط¹ط§طھ"""
    cart = get_object_or_404(Cart, user=request.user, is_active=True)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.error(request, 'ط§ظ„ط³ظ„ط© ظپط§ط±ط؛ط©. ظ„ط§ ظٹظ…ظƒظ† ط¥طھظ…ط§ظ… ط§ظ„ط´ط±ط§ط،.')
        return redirect('stores:cart_detail')
    
    if request.method == 'POST':
        errors = []
        sales_created = []
        
        # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† طھظˆظپط± ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ†طھط¬ط§طھ ظ‚ط¨ظ„ ط¥ظ†ط´ط§ط، ط§ظ„ظ…ط¨ظٹط¹ط§طھ
        for item in cart_items:
            if item.size:
                # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ„ظ„ظ…ظ‚ط§ط³ ط§ظ„ظ…ط­ط¯ط¯
                try:
                    size_stock = item.product.size_stocks.get(size=item.size)
                    if item.quantity > size_stock.stock:
                        errors.append(f'ط§ظ„ظ…ظ†طھط¬ {item.product.name} - ط§ظ„ظ…ظ‚ط§ط³ {item.size}: ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ‡ظٹ {size_stock.stock} ظ‚ط·ط¹ط© ظپظ‚ط·.')
                        continue
                except ProductSizeStock.DoesNotExist:
                    errors.append(f'ط§ظ„ظ…ظ†طھط¬ {item.product.name} - ط§ظ„ظ…ظ‚ط§ط³ {item.size}: ط؛ظٹط± ظ…طھظˆظپط±.')
                    continue
            else:
                # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ط¥ط¬ظ…ط§ظ„ظٹط©
                if item.quantity > item.product.stock:
                    errors.append(f'ط§ظ„ظ…ظ†طھط¬ {item.product.name}: ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ‡ظٹ {item.product.stock} ظ‚ط·ط¹ط© ظپظ‚ط·.')
                    continue
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('stores:cart_detail')
        
        # ط¥ظ†ط´ط§ط، ط³ط¬ظ„ط§طھ ط§ظ„ظ…ط¨ظٹط¹ط§طھ ظˆطھط­ط¯ظٹط« ط§ظ„ظ…ط®ط²ظˆظ†
        for item in cart_items:
            # ط¥ظ†ط´ط§ط، ط³ط¬ظ„ ط§ظ„ظ…ط¨ظٹط¹ط©
            sale = Sale.objects.create(
                store=item.product.store,
                product=item.product,
                buyer=request.user,
                size=item.size if item.size else '',
                quantity=item.quantity,
                price=item.product.price
            )
            sales_created.append(sale)
            
            # طھط­ط¯ظٹط« ط§ظ„ظ…ط®ط²ظˆظ†
            if item.size:
                # طھط­ط¯ظٹط« ظƒظ…ظٹط© ط§ظ„ظ…ظ‚ط§ط³ ط§ظ„ظ…ط­ط¯ط¯
                try:
                    size_stock = item.product.size_stocks.get(size=item.size)
                    if size_stock.stock >= item.quantity:
                        size_stock.stock -= item.quantity
                        size_stock.save()
                        # طھط­ط¯ظٹط« ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ظƒظ…ظٹط© ظپظٹ Product
                        item.product.stock = item.product.get_total_stock()
                        item.product.save()
                    else:
                        errors.append(f'ط®ط·ط£ ظپظٹ طھط­ط¯ظٹط« ط§ظ„ظ…ط®ط²ظˆظ† ظ„ظ„ظ…ظ†طھط¬ {item.product.name} - ط§ظ„ظ…ظ‚ط§ط³ {item.size}')
                except ProductSizeStock.DoesNotExist:
                    errors.append(f'ط§ظ„ظ…ظ‚ط§ط³ {item.size} ط؛ظٹط± ظ…ظˆط¬ظˆط¯ ظ„ظ„ظ…ظ†طھط¬ {item.product.name}')
            else:
                # طھط­ط¯ظٹط« ط§ظ„ظƒظ…ظٹط© ط§ظ„ط¥ط¬ظ…ط§ظ„ظٹط©
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
                else:
                    errors.append(f'ط®ط·ط£ ظپظٹ طھط­ط¯ظٹط« ط§ظ„ظ…ط®ط²ظˆظ† ظ„ظ„ظ…ظ†طھط¬ {item.product.name}')
        
        if errors:
            # ط¥ط°ط§ ط­ط¯ط« ط®ط·ط£طŒ ط§ط­ط°ظپ ط§ظ„ظ…ط¨ظٹط¹ط§طھ ط§ظ„طھظٹ طھظ… ط¥ظ†ط´ط§ط¤ظ‡ط§
            for sale in sales_created:
                sale.delete()
            for error in errors:
                messages.error(request, error)
            return redirect('stores:cart_detail')
        
        # ط­ط°ظپ ط¹ظ†ط§طµط± ط§ظ„ط³ظ„ط© ط¨ط¹ط¯ ط¥طھظ…ط§ظ… ط§ظ„ط´ط±ط§ط،
        cart_items.delete()
        cart.is_active = False
        cart.save()
        
        messages.success(request, f'طھظ… ط¥طھظ…ط§ظ… ط§ظ„ط´ط±ط§ط، ط¨ظ†ط¬ط§ط­! طھظ… ط¥ظ†ط´ط§ط، {len(sales_created)} ط¹ظ…ظ„ظٹط© ط¨ظٹط¹.')
        return redirect('stores:cart_detail')
    
    # ط¥ط°ط§ ظ„ظ… ظٹظƒظ† POSTطŒ ط¥ط¹ط§ط¯ط© طھظˆط¬ظٹظ‡ ط¥ظ„ظ‰ ط§ظ„ط³ظ„ط©
    return redirect('stores:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'السلة متاحة للمستخدم العادي فقط.')
        return redirect('home')


    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('stores:cart_detail')


@login_required
def update_cart_item(request, item_id):
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'السلة متاحة للمستخدم العادي فقط.')
        return redirect('home')


    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = cart_item.product
    
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'طھظ… ط­ط°ظپ ط§ظ„ظ…ظ†طھط¬ ظ…ظ† ط§ظ„ط³ظ„ط©.')
        else:
            # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ط­ط³ط¨ ط§ظ„ظ…ظ‚ط§ط³
            if cart_item.size:
                # ط¥ط°ط§ ظƒط§ظ† ظ‡ظ†ط§ظƒ ظ…ظ‚ط§ط³ ظ…ط­ط¯ط¯طŒ طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ„ظ‡ط°ط§ ط§ظ„ظ…ظ‚ط§ط³
                try:
                    size_stock = product.size_stocks.get(size=cart_item.size)
                    max_quantity = size_stock.stock
                    
                    # ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ظƒظ…ظٹط© ظپظٹ ط§ظ„ط³ظ„ط© ط§ظ„ط­ط§ظ„ظٹط© (ط¨ط§ط³طھط«ظ†ط§ط، ط§ظ„ط¹ظ†طµط± ط§ظ„ط­ط§ظ„ظٹ)
                    other_items = CartItem.objects.filter(
                        cart=cart_item.cart,
                        product=product,
                        size=cart_item.size
                    ).exclude(id=cart_item.id)
                    reserved_quantity = sum(item.quantity for item in other_items)
                    available_quantity = max_quantity - reserved_quantity
                    
                    if quantity > available_quantity:
                        messages.error(request, f'ط¹ط°ط±ط§ظ‹طŒ ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ„ظ„ظ…ظ‚ط§ط³ {cart_item.size} ظ‡ظٹ {available_quantity} ظ‚ط·ط¹ط© ظپظ‚ط·.')
                    else:
                        cart_item.quantity = quantity
                        cart_item.save()
                        messages.success(request, 'طھظ… طھط­ط¯ظٹط« ط§ظ„ظƒظ…ظٹط© ط¨ظ†ط¬ط§ط­.')
                except ProductSizeStock.DoesNotExist:
                    messages.error(request, 'ط§ظ„ظ…ظ‚ط§ط³ ط§ظ„ظ…ط­ط¯ط¯ ط؛ظٹط± ظ…ظˆط¬ظˆط¯.')
            else:
                # ط¥ط°ط§ ظ„ظ… ظٹظƒظ† ظ‡ظ†ط§ظƒ ظ…ظ‚ط§ط³ ظ…ط­ط¯ط¯طŒ ط§ط³طھط®ط¯ظ… ط§ظ„ظƒظ…ظٹط© ط§ظ„ط¥ط¬ظ…ط§ظ„ظٹط©
                if quantity > product.stock:
                    messages.error(request, f'ط¹ط°ط±ط§ظ‹طŒ ط§ظ„ظƒظ…ظٹط© ط§ظ„ظ…طھط§ط­ط© ظ‡ظٹ {product.stock} ظ‚ط·ط¹ط© ظپظ‚ط·.')
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, 'طھظ… طھط­ط¯ظٹط« ط§ظ„ظƒظ…ظٹط© ط¨ظ†ط¬ط§ط­.')
    
    return redirect('stores:cart_detail')


@login_required
def toggle_favorite_product(request, product_id):
    """ط¥ط¶ط§ظپط© ط£ظˆ ط­ط°ظپ ظ…ظ†طھط¬ ظ…ظ† ط§ظ„ظ…ظپط¶ظ„ط©."""
    if request.user.is_admin() or request.user.is_store_owner():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'is_favorite': False}, status=403)
        messages.error(request, 'ط§ظ„ظ…ظپط¶ظ„ط© ظ…طھط§ط­ط© ظ„ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط¹ط§ط¯ظٹ ظپظ‚ط·.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    product = get_object_or_404(
        Product,
        id=product_id,
        store__approval_status='approved',
        store__is_active=True
    )
    favorite, created = FavoriteProduct.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    return redirect(request.META.get('HTTP_REFERER', 'stores:favorite_products'))


@login_required
def favorite_products(request):
    """ط¹ط±ط¶ ط§ظ„ظ…ظ†طھط¬ط§طھ ط§ظ„ظ…ظپط¶ظ„ط© ظ„ظ„ظ…ط³طھط®ط¯ظ…."""
    if request.user.is_admin() or request.user.is_store_owner():
        messages.error(request, 'طµظپط­ط© ط§ظ„ظ…ظپط¶ظ„ط© ظ…طھط§ط­ط© ظ„ظ„ظ…ط³طھط®ط¯ظ… ط§ظ„ط¹ط§ط¯ظٹ ظپظ‚ط·.')
        return redirect('home')

    favorites = FavoriteProduct.objects.filter(
        user=request.user
    ).select_related('product', 'product__store').order_by('-created_at')

    products = [fav.product for fav in favorites]
    return render(request, 'stores/favorite_products.html', {
        'favorite_products': products,
        'favorite_count': len(products)
    })


@login_required
def rate_store(request, store_id):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    store = get_object_or_404(Store, id=store_id, approval_status='approved')
    if store.owner_id == request.user.id:
        messages.error(request, 'ظ„ط§ ظٹظ…ظƒظ†ظƒ طھظ‚ظٹظٹظ… ظ…طھط¬ط±ظƒ.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    rating_obj, _ = StoreRating.objects.get_or_create(user=request.user, store=store)
    form = StoreRatingForm(request.POST, instance=rating_obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'طھظ… ط­ظپط¸ طھظ‚ظٹظٹظ… ط§ظ„ظ…طھط¬ط±.')
    else:
        messages.error(request, 'طھط¹ط°ط± ط­ظپط¸ طھظ‚ظٹظٹظ… ط§ظ„ظ…طھط¬ط±. طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ط¨ظٹط§ظ†ط§طھ.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def rate_product(request, product_id):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    product = get_object_or_404(Product, id=product_id, store__approval_status='approved')
    if product.store.owner_id == request.user.id:
        messages.error(request, 'ظ„ط§ ظٹظ…ظƒظ†ظƒ طھظ‚ظٹظٹظ… ظ…ظ†طھط¬ ظ…ظ† ظ…طھط¬ط±ظƒ.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    rating_obj, _ = ProductRating.objects.get_or_create(user=request.user, product=product)
    form = ProductRatingForm(request.POST, instance=rating_obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'طھظ… ط­ظپط¸ طھظ‚ظٹظٹظ… ط§ظ„ظ…ظ†طھط¬.')
    else:
        messages.error(request, 'طھط¹ط°ط± ط­ظپط¸ طھظ‚ظٹظٹظ… ط§ظ„ظ…ظ†طھط¬. طھط­ظ‚ظ‚ ظ…ظ† ط§ظ„ط¨ظٹط§ظ†ط§طھ.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))




def store_offers(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    products = Product.objects.filter(
        store=store,
        original_price__isnull=False,
        price__lt=F('original_price')
    )

    return render(request, 'stores/store_offers.html', {
        'store': store,
        'products': products
    })