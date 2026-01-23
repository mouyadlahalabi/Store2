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

 
    # 🔹 لوحة المدير
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    



    # 🔹 إنشاء مدير جديد
    path('create-admin/', views.create_admin, name='create_admin'),
]
