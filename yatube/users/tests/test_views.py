from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User, CreationForm


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petr')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_users_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self) -> None:
        """Шаблон signup сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('users:signup')))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CreationForm)
