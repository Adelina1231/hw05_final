from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import User


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='User')
        '''cls.form = CreationForm()'''

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_guest_client_signup(self) -> None:
        """Валидная форма создает аккаунт."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Petr',
            'last_name': 'Petrovich',
            'username': 'P.Petrovich',
            'email': 'P.Petrovich@test.ru',
            'password1': 'test!123457',
            'password2': 'test!123457',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Petr',
                last_name='Petrovich',
                username='P.Petrovich',
                email='P.Petrovich@test.ru'
            ).exists()
        )
