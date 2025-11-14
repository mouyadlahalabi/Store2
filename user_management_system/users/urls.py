from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # 🔹 حسابات المستخدمين
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # 🔹 لوحة التحكم الشخصية
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),

    # 🔹 المتاجر الخاصة بالمستخدم
    # path('my-stores/', views.store_list_user, name='store_list_user'),
    # path('my-stores/create/', views.create_store, name='create_store'),
    # path('my-stores/<int:store_id>/', views.store_detail, name='store_detail'),
    # path('my-stores/<int:store_id>/edit/', views.edit_store, name='edit_store'),
    # path('my-stores/<int:store_id>/delete/', views.store_delete, name='store_delete'),

    # # 🔹 المتاجر العامة
    # path('stores/', views.store_list, name='store_list_user'),

    # 🔹 لوحة المدير
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    # path('manage-stores/', views.manage_stores, name='manage_stores'),

    # # 🔹 طلبات المتاجر
    # path('store-requests/', views.store_requests, name='store_requests'),
    # path('store/<int:store_id>/approve/', views.approve_store, name='approve_store'),
    # path('store/<int:store_id>/reject/', views.reject_store, name='reject_store'),
    # path('store/<int:store_id>/admin-detail/', views.store_detail_admin, name='store_detail_admin'),
    # path('store/<int:store_id>/verify/', views.verify_store, name='verify_store'),


    # 🔹 إنشاء مدير جديد
    path('create-admin/', views.create_admin, name='create_admin'),
]
