from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User, UserProfile


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """إنشاء مجموعات المستخدمين عند تطبيق الهجرات"""
    if sender.name == 'users':
        # إنشاء مجموعات المستخدمين
        Group.objects.get_or_create(name='Admins')
        Group.objects.get_or_create(name='Users')
        Group.objects.get_or_create(name='Store Owners')


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """إضافة المستخدم إلى المجموعة المناسبة عند إنشائه"""
    if created:
        if instance.user_type == 'admin':
            group, _ = Group.objects.get_or_create(name='Admins')
        elif instance.user_type == 'store_owner':
            group, _ = Group.objects.get_or_create(name='Store Owners')
        else:
            group, _ = Group.objects.get_or_create(name='Users')
        
        instance.groups.add(group)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """إنشاء ملف شخصي للمستخدم عند إنشائه"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
