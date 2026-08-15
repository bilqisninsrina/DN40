from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Registration

class RegistrationFlowTests(TestCase):
    def test_home_is_public(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'DIES')
        self.assertContains(response, 'navbar')
        self.assertContains(response, 'package-list')

    def test_login_uses_home_page_as_blurred_background(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'login-background')
        self.assertContains(response, 'Kategori Paket')
        self.assertContains(response, 'Register or Login')
        self.assertContains(response, 'email-button')
        self.assertContains(response, 'sso-button')

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


class PurchaseFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer@example.com',
            email='buyer@example.com',
            password='aman-sekali',
        )
        self.client.force_login(self.user)

    def registration_data(self, **overrides):
        data = {
            'full_name': 'Budi Fasilkom',
            'whatsapp_number': '081234567890',
            'cohort_year': 2020,
            'study_program': Registration.StudyProgram.ILMU_KOMPUTER,
            'ticket_quantity': 1,
            'shirt_size': Registration.ShirtSize.M,
        }
        data.update(overrides)
        return data

    def test_alumni_registration_has_fixed_quantity_and_price(self):
        response = self.client.post(
            reverse('buy', args=['alumni']),
            self.registration_data(ticket_quantity=8),
        )
        registration = Registration.objects.get()
        self.assertRedirects(response, reverse('history'))
        self.assertEqual(registration.ticket_quantity, 1)
        self.assertEqual(registration.total_price, 275_000)

    def test_non_package_total_uses_ticket_quantity(self):
        data = self.registration_data(ticket_quantity=4)
        data.pop('shirt_size')
        response = self.client.post(reverse('buy', args=['non-paket']), data)
        registration = Registration.objects.get()
        self.assertRedirects(response, reverse('history'))
        self.assertEqual(registration.shirt_size, '')
        self.assertEqual(registration.total_price, 200_000)

    def test_whatsapp_rejects_non_numeric_characters(self):
        response = self.client.post(
            reverse('buy', args=['mahasiswa']),
            self.registration_data(whatsapp_number='+62 812-345'),
        )
        self.assertContains(response, 'hanya boleh berisi angka')
        self.assertFalse(Registration.objects.exists())

    def test_staff_can_download_filterable_excel(self):
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        response = self.client.get(reverse('export_registrations'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertTrue(response.content.startswith(b'PK'))
