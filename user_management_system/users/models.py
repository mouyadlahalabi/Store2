from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # ✅ بدلاً من from stores.models import Store


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'مدير النظام'),
        ('user', 'مستخدم عادي'),
        ('store_owner', 'صاحب متجر'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name='نوع المستخدم'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='رقم الهاتف'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='العنوان'
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاريخ الميلاد'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='صورة الملف الشخصي'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='مُتحقق منه'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
        
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_store_owner(self):
        return self.user_type == 'store_owner'
    
    def is_regular_user(self):
        return self.user_type == 'user'


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='المستخدم'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='نبذة شخصية'
    )
    
    website = models.URLField(
        blank=True,
        verbose_name='الموقع الإلكتروني'
    )
    
    social_media_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='روابط وسائل التواصل الاجتماعي'
    )
    
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='التفضيلات'
    )
    
    class Meta:
        verbose_name = 'الملف الشخصي'
        verbose_name_plural = 'الملفات الشخصية'
        
    def __str__(self):
        return f"ملف {self.user.username} الشخصي"
