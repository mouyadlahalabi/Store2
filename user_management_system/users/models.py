from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    نموذج المستخدم المخصص مع أنواع المستخدمين المختلفة
    """
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
        """التحقق من كون المستخدم مدير نظام"""
        return self.user_type == 'admin'
    
    def is_store_owner(self):
        """التحقق من كون المستخدم صاحب متجر"""
        return self.user_type == 'store_owner'
    
    def is_regular_user(self):
        """التحقق من كون المستخدم عادي"""
        return self.user_type == 'user'


class UserProfile(models.Model):
    """
    ملف شخصي إضافي للمستخدم
    """
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


class Store(models.Model):
    """
    نموذج المتجر لأصحاب المتاجر
    """
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'في انتظار الموافقة'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'store_owner'},
        related_name='store',
        verbose_name='صاحب المتجر'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='اسم المتجر'
    )
    
    description = models.TextField(
        verbose_name='وصف المتجر'
    )
    
    logo = models.ImageField(
        upload_to='store_logos/',
        blank=True,
        null=True,
        verbose_name='شعار المتجر'
    )
    
    address = models.TextField(
        verbose_name='عنوان المتجر'
    )
    
    phone = models.CharField(
        max_length=15,
        verbose_name='هاتف المتجر'
    )
    
    email = models.EmailField(
        verbose_name='بريد المتجر الإلكتروني'
    )
    
    website = models.URLField(
        blank=True,
        verbose_name='موقع المتجر'
    )
    
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الموافقة'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='متحقق منه'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'admin'},
        related_name='approved_stores',
        verbose_name='تمت الموافقة بواسطة'
    )
    
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ الموافقة'
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='سبب الرفض'
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
        verbose_name = 'متجر'
        verbose_name_plural = 'المتاجر'
        
    def __str__(self):
        return self.name