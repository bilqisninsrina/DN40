from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class RegistrationFlowTests(TestCase):
    def test_home_is_public(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'DIES')
        self.assertContains(response, 'nav-main')
        self.assertContains(response, 'package-list')

    def test_login_uses_home_page_as_blurred_background(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'login-home-background')
        self.assertContains(response, 'Kategori Paket')
        self.assertContains(response, 'Register or Login')

    def test_alumni_can_register_with_email(self):
        response = self.client.post(
            reverse('login'),
            {
                'email': 'alumni@example.com',
                'password': 'aman-sekali',
            },
            follow=True,
        )
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='alumni@example.com').exists())

    def test_buy_requires_login(self):
        response = self.client.get(reverse('buy', args=['alumni']))
        login_url = reverse('login')
        buy_url = reverse('buy', args=['alumni'])
        self.assertRedirects(response, f'{login_url}?next={buy_url}')

    def test_sso_without_configuration_returns_guidance(self):
        response = self.client.get(reverse('sso_start'), follow=True)
        self.assertContains(response, 'SSO UI belum dikonfigurasi')
