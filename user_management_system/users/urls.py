from django.urls import path
from . import views

urlpatterns = [
    # الصفحات العامة
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # لوحة التحكم والملف الشخصي
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # إدارة المتاجر
    path('store/create/', views.create_store, name='create_store'),
    path('store/', views.store_detail, name='store_detail'),
    path('store/edit/', views.edit_store, name='edit_store'),
    
    # لوحة تحكم المديرين
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/store/', views.manage_stores, name='manage_stores'),
    path('admin/stores/<int:store_id>/verify/', views.verify_store, name='verify_store'),
    path('admin/create-admin/', views.create_admin, name='create_admin'),
    
    # إدارة طلبات المتاجر
    path('store-requests/', views.store_requests, name='store_requests'),
    path('store-requests/<int:store_id>/approve/', views.approve_store, name='approve_store'),
    path('store-requests/<int:store_id>/reject/', views.reject_store, name='reject_store'),
    path('store-requests/<int:store_id>/detail/', views.store_detail_admin, name='store_detail_admin'),
    
    
    path('stores/', views.store_list, name='store_list'),
    path('stores/delete/<int:store_id>/', views.store_delete, name='store_delete'),]