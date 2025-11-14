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
from stores.models import Store, Product, FavoriteStore
from random import sample
@login_required(login_url='login') 
def home(request):
    """الصفحة الرئيسية - عرض المتاجر ومنتجات عشوائية من كل متجر"""
    # جلب المتاجر المعتمدة والنشطة فقط
    stores = Store.objects.filter(
        is_active=True, 
        approval_status='approved'
    ).prefetch_related('products')

    # فلتر حسب المتجر
    store_filter = request.GET.get('store')
    if store_filter:
        stores = stores.filter(id=store_filter)

    store_products = []
    # جلب جميع المتاجر المفضلة للمستخدم
    favorite_store_ids = set()
    if request.user.is_authenticated:
        favorite_store_ids = set(
            FavoriteStore.objects.filter(user=request.user).values_list('store_id', flat=True)
        )
    
    for store in stores:
        # جلب المنتجات الموجودة فقط (تجنب المنتجات المحذوفة)
        products = list(Product.objects.filter(store=store))
        if products:
            # جلب 4-6 منتجات عشوائية من كل متجر
            num_products = min(len(products), 6)
            if num_products > 0:
                random_products = sample(products, num_products)
                store_products.append({
                    'store': store,
                    'products': random_products,
                    'is_favorite': store.id in favorite_store_ids
                })

    # جلب جميع المتاجر للفلتر
    all_stores = Store.objects.filter(
        is_active=True, 
        approval_status='approved'
    ).order_by('name')
    
    # جلب المتاجر المفضلة للمستخدم
    favorite_store_ids = set()
    if request.user.is_authenticated and not request.user.is_store_owner():
        
        favorite_store_ids = set(
            FavoriteStore.objects.filter(user=request.user)
            .values_list('store_id', flat=True)
        )

    context = {
        'store_products': store_products,
        'all_stores': all_stores,
        'selected_store': int(store_filter) if store_filter else None,
        'favorite_store_ids': favorite_store_ids,
    }
    return render(request, 'users/home.html', context)



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


# @login_required
# def create_store(request):
#     """إنشاء متجر جديد مرتبط بالمستخدم"""
#     if not request.user.is_store_owner():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     if request.method == 'POST':
#         form = StoreCreationForm(request.POST, request.FILES)
#         if form.is_valid():
#             store = form.save(commit=False)
#             store.owner = request.user  # ربط المتجر بالمستخدم الحالي
#             store.save()
#             messages.success(request, 'تم إنشاء المتجر بنجاح!')
#             return redirect('store_list_user')
#     else:
#         form = StoreCreationForm()

#     return render(request, 'users/create_store.html', {'form': form})


# @login_required
# def store_list_user(request):
#     """عرض جميع المتاجر الخاصة بالمستخدم الحالي"""
#     stores = Store.objects.filter(owner=request.user)
#     return render(request, 'users/store_list_user.html', {'stores': stores})


# @login_required
# def store_detail(request, store_id):
#     """عرض تفاصيل متجر معين"""
#     store = get_object_or_404(Store, id=store_id, owner=request.user)
#     return render(request, 'users/store_detail.html', {'store': store})


# @login_required
# def edit_store(request, store_id):
#     """تعديل متجر"""
#     store = get_object_or_404(Store, id=store_id, owner=request.user)

#     if request.method == 'POST':
#         form = StoreCreationForm(request.POST, request.FILES, instance=store)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'تم تحديث المتجر بنجاح.')
#             return redirect('store_detail', store_id=store.id)
#     else:
#         form = StoreCreationForm(instance=store)

#     return render(request, 'users/edit_store.html', {'form': form, 'store': store})


# @login_required
# def store_delete(request, store_id):
#     """حذف متجر"""
#     store = get_object_or_404(Store, id=store_id, owner=request.user)

#     if request.method == 'POST':
#         store.delete()
#         messages.success(request, 'تم حذف المتجر بنجاح.')
#         return redirect('store_list_user')

#     messages.error(request, 'لا يمكن حذف المتجر عبر الرابط مباشرة.')
#     return redirect('store_list_user')


@login_required
def admin_dashboard(request):
    """لوحة تحكم المديرين"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    context = {
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(user_type='admin').count(),
        'total_regular_users': User.objects.filter(user_type='user').count(),
        'total_store_owners': User.objects.filter(user_type='store_owner').count(),
        'total_stores': Store.objects.count(),
        'verified_stores': Store.objects.filter(is_verified=True).count(),
        'pending_stores_count': Store.objects.filter(approval_status='pending').count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_stores': Store.objects.order_by('-created_at')[:5],
    }

    return render(request, 'users/admin_dashboard.html', context)


@login_required
def manage_users(request):
    """إدارة المستخدمين (للمديرين فقط)"""
    if not request.user.is_admin():
        return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {'users': users})


# @login_required
# def manage_stores(request):
#     """إدارة المتاجر (للمديرين فقط)"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     stores = Store.objects.all().order_by('-created_at')
#     return render(request, 'users/manage_stores.html', {'stores': stores})


# @login_required
# def verify_store(request, store_id):
#     """التحقق من المتجر (للمديرين فقط)"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     store = get_object_or_404(Store, id=store_id)
#     store.is_verified = not store.is_verified
#     store.save()

#     status = 'تم التحقق من' if store.is_verified else 'تم إلغاء التحقق من'
#     messages.success(request, f'{status} المتجر {store.name}.')

#     return redirect('manage_stores')


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


# @login_required
# def store_requests(request):
#     """عرض طلبات المتاجر المعلقة"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     pending_stores = Store.objects.filter(approval_status='pending').order_by('-created_at')
#     approved_stores = Store.objects.filter(approval_status='approved').order_by('-approval_date')
#     rejected_stores = Store.objects.filter(approval_status='rejected').order_by('-updated_at')

#     context = {
#         'pending_stores': pending_stores,
#         'approved_stores': approved_stores,
#         'rejected_stores': rejected_stores,
#         'pending_count': pending_stores.count(),
#         'approved_count': approved_stores.count(),
#         'rejected_count': rejected_stores.count(),
#     }

#     return render(request, 'users/store_requests.html', context)


# @login_required
# def approve_store(request, store_id):
#     """الموافقة على متجر"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     store = get_object_or_404(Store, id=store_id)

#     if request.method == 'POST':
#         store.approval_status = 'approved'
#         store.is_verified = True
#         store.approved_by = request.user
#         store.approval_date = timezone.now()
#         store.rejection_reason = ''
#         store.save()

#         messages.success(request, f'تمت الموافقة على متجر "{store.name}" بنجاح!')
#         return redirect('store_requests')

#     return render(request, 'users/approve_store.html', {'store': store})


# @login_required
# def reject_store(request, store_id):
#     """رفض متجر"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     store = get_object_or_404(Store, id=store_id)

#     if request.method == 'POST':
#         rejection_reason = request.POST.get('rejection_reason', '')

#         if not rejection_reason.strip():
#             messages.error(request, 'يجب إدخال سبب الرفض.')
#             return render(request, 'users/reject_store.html', {'store': store})

#         store.approval_status = 'rejected'
#         store.is_verified = False
#         store.approved_by = request.user
#         store.approval_date = timezone.now()
#         store.rejection_reason = rejection_reason
#         store.save()

#         messages.success(request, f'تم رفض متجر "{store.name}".')
#         return redirect('store_requests')

#     return render(request, 'users/reject_store.html', {'store': store})


# @login_required
# def store_detail_admin(request, store_id):
#     """عرض تفاصيل المتجر للمديرين"""
#     if not request.user.is_admin():
#         return HttpResponseForbidden('غير مسموح لك بالوصول إلى هذه الصفحة.')

#     store = get_object_or_404(Store, id=store_id)

#     context = {
#         'store': store,
#         'can_approve': store.approval_status == 'pending',
#         'can_reject': store.approval_status == 'pending',
#     }

#     return render(request, 'users/store_detail_admin.html', context)


# def store_list(request):
#     """عرض جميع المتاجر العامة"""
#     stores = Store.objects.filter(is_verified=True)
#     return render(request, 'users/store_list_user.html', {'stores': stores})
