from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from stores.models import Store

User = get_user_model()

class HomeViewRedirectTests(TestCase):
    def setUp(self):
        # المستخدم العادي
        self.regular = User.objects.create_user(
            username='user1', password='pass', user_type='user'
        )
        # صاحب متجر
        self.owner = User.objects.create_user(
            username='owner1', password='pass', user_type='store_owner'
        )
        # إنشاء متجر مرتبط بصاحب المتجر
        self.store = Store.objects.create(
            name='Test Store', owner=self.owner,
            approval_status='approved', is_active=True
        )
        # مدير النظام
        self.admin = User.objects.create_user(
            username='admin1', password='pass', user_type='admin'
        )

    def test_regular_user_sees_home(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/home.html')

    def test_store_owner_redirects_to_store(self):
        self.client.login(username='owner1', password='pass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('stores:my_store_front'))

    def test_admin_redirects_to_dashboard(self):
        self.client.login(username='admin1', password='pass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_nav_links_for_regular_user(self):
        # regular user should see 'المتاجر' link
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'المتاجر')
        self.assertNotContains(response, 'المبيعات')

    def test_nav_links_for_store_owner(self):
        self.client.login(username='owner1', password='pass')
        response = self.client.get(reverse('stores:my_store_front'))
        self.assertContains(response, 'المبيعات')
        self.assertNotContains(response, 'المتاجر')
