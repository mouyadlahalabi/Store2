from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile

from stores.models import Store  # ✅ استيراد المتجر من التطبيق الصحيح



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إدارة المستخدمين في لوحة الإدارة"""
    
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('معلومات إضافية'), {
            'fields': ('user_type', 'phone_number', 'address', 'date_of_birth', 
                      'profile_picture', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('معلومات إضافية'), {
            'fields': ('user_type', 'phone_number', 'address', 'date_of_birth', 
                      'profile_picture', 'is_verified')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """إدارة الملفات الشخصية في لوحة الإدارة"""
    
    list_display = ('user', 'website')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('user__user_type',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """إدارة المتاجر في لوحة الإدارة"""
    
    list_display = ('name', 'owner', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'owner__username', 'email', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('owner', 'name', 'description', 'logo')
        }),
        (_('معلومات الاتصال'), {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        (_('الحالة'), {
            'fields': ('is_active', 'is_verified')
        }),
    )


