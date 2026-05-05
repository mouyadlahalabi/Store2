from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponseForbidden

from django import forms
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    UserProfileForm,
    
    PasswordChangeForm
)
from .models import User 
from stores.models import (
    Store,
    Product,
    Sale,
    FavoriteProduct,
    StoreRating,
    ProductRating,
)
from random import sample
from random import sample
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F, Q, Sum


@login_required(login_url='login')
def home(request):
    """عرض الصفحة الرئيسية.

    السلوك الجديد:
    * المستخدم العادي يبقى على الواجهة الحالية (قائمة المنتجات والمتاجر).
    * صاحب المتجر يُعاد توجيهه إلى واجهة متجره الخاص.
    * المدير (admin) يُعاد توجيهه إلى لوحة الإدارة.
    """
    # إذا تم تسجيل الدخول، نفحص نوع المستخدم ونوجهه للصفحة المناسبة
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        elif request.user.is_store_owner():
            # واجهة صاحب المتجر هي صفحة متجره الأمامية
            return redirect('stores:my_store_front')

    stores = Store.objects.filter(is_active=True, approval_status='approved').prefetch_related('products')

    # فلتر المتجر
    store_filter = request.GET.get('store')
    if store_filter:
        stores = stores.filter(id=store_filter)

    # فلتر البحث
    query = request.GET.get('q', '').strip()

    # ترتيب المنتجات
    order = request.GET.get('order')

    favorite_product_ids = set()
    if request.user.is_authenticated and not request.user.is_store_owner():
        favorite_product_ids = set(
            FavoriteProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    store_products = []

    for store in stores:
        products_qs = store.products.all()

        # فلتر البحث
        if query:
            products_qs = products_qs.filter(
                name__icontains=query
            ) | products_qs.filter(
                description__icontains=query
            )

        # ترتيب المنتجات
        if order == 'newest':
            products_qs = products_qs.order_by('-created_at')
        elif order == 'price-low':
            products_qs = products_qs.order_by('price')
        elif order == 'price-high':
            products_qs = products_qs.order_by('-price')
        elif order == 'popular':
            products_qs = products_qs.order_by('-sales_count')

        products_list = list(products_qs)
        if products_list:
            if not query:
                products_list = sample(products_list, min(len(products_list), 6))
            else:
                products_list = products_list[:6]

            if favorite_product_ids:
                for product in products_list:
                    product.is_favorite = product.id in favorite_product_ids

            store_products.append({
                'store': store,
                'products': products_list,
                'is_favorite': False
            })

    # -----------------------
    # إضافة منتجات العروض فقط
    # -----------------------
    discounted_store_products = []
    for store in stores:
        discounted_qs = store.products.filter(original_price__gt=F('price'))
        
        # يمكن فلتر البحث والعرض حسب الحاجة
        if query:
            discounted_qs = discounted_qs.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        # ترتيب المنتجات المخفضة
        if order == 'newest':
            discounted_qs = discounted_qs.order_by('-created_at')
        elif order == 'price-low':
            discounted_qs = discounted_qs.order_by('price')
        elif order == 'price-high':
            discounted_qs = discounted_qs.order_by('-price')
        elif order == 'popular':
            discounted_qs = discounted_qs.order_by('-sales_count')

        discounted_list = list(discounted_qs)
        if discounted_list:
            discounted_list = discounted_list[:6]  # عرض 6 منتجات كحد أقصى لكل متجر
            if favorite_product_ids:
                for product in discounted_list:
                    product.is_favorite = product.id in favorite_product_ids
            discounted_store_products.append({
                'store': store,
                'products': discounted_list,
                'is_favorite': False
            })

    all_stores = Store.objects.filter(is_active=True, approval_status='approved').order_by('name')

    context = {
        'store_products': store_products,
        'discounted_store_products': discounted_store_products,  # <--- هذه للعروض
        'all_stores': all_stores,
        'selected_store': int(store_filter) if store_filter else None,
        'search_query': query,
        'order': order,
        'favorite_product_ids': favorite_product_ids,
    }
    return render(request, 'users/home.html', context)



def about_page(request):
    """صفحة حول المتجر"""
    return render(request, 'users/about.html')


def register(request):
    """تسجيل مستخدم جديد"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً {user.first_name}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    # ✅ اجلب جميع المتاجر التابعة للمستخدم
    stores = Store.objects.filter(owner=user)

    context = {
        'user': user,
        'stores': stores,  # الآن stores هي قائمة من المتاجر
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    """عرض وتحديث الملف الشخصي"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})


@login_required
def change_password(request):
    """تغيير كلمة المرور"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})




@login_required
def admin_dashboard(request):
    """لوحة تحكم المديرين"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    revenue_data = Sale.objects.aggregate(total=Sum(F('quantity') * F('price')))

    context = {
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(user_type='admin').count(),
        'total_regular_users': User.objects.filter(user_type='user').count(),
        'total_store_owners': User.objects.filter(user_type='store_owner').count(),
        'total_stores': Store.objects.count(),
        'total_products': Product.objects.count(),
        'total_sales': Sale.objects.count(),
        'total_revenue': revenue_data['total'] or 0,
        'total_product_favorites': FavoriteProduct.objects.count(),
        'total_store_ratings': StoreRating.objects.count(),
        'total_product_ratings': ProductRating.objects.count(),
        'verified_stores': Store.objects.filter(is_verified=True).count(),
        'pending_stores_count': Store.objects.filter(approval_status='pending').count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_stores': Store.objects.order_by('-created_at')[:5],
        'recent_sales': Sale.objects.select_related('buyer', 'product', 'store').order_by('-created_at')[:5],
    }

    return render(request, 'users/admin_dashboard.html', context)


@login_required
def manage_users(request):
    """إدارة المستخدمين (للمديرين فقط)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {'users': users})




@login_required
def create_admin(request):
    """إنشاء حساب مدير جديد"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()

            messages.success(request, f'تم إنشاء حساب المدير {user.username} بنجاح!')
            return redirect('manage_users')
    else:
        form = CustomUserCreationForm()
        form.fields['user_type'].widget = forms.HiddenInput()
        form.fields['user_type'].initial = 'admin'

    return render(request, 'users/create_admin.html', {'form': form})
