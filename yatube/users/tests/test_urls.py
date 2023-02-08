from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import User


class PostURLTest(TestCase):
    @classmethod
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='HasNoName')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_url(self) -> None:
        """Страница /auth/signup/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_url(self) -> None:
        """Страница /auth/login/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/login/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_url(self) -> None:
        """Страница /auth/password_reset/ доступна любому пользователю."""
        response = self.guest_client.get('/auth/password_reset/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_done_url(self) -> None:
        """Страница /auth/password_reset/done/ доступна любому пользователю."""
        response = self.authorized_client.get('/auth/password_reset/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url(self) -> None:
        """Страница /auth/password_change/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/auth/password_change/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_done_url(self) -> None:
        """Страница /auth/password_change/done/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/auth/password_change/done/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_url(self) -> None:
        """Страница /auth/logout/ доступна авторизованному
           пользователю."""
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_url_redirect_anonymous_on_admin_login(self):
        """Страница /auth/password_change/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/')

    def test_password_change_done_url_redirect_anonymous_on_admin_login(self):
        """Страница /auth/password_change/done/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/done/',
                                         follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/auth/password_change/done/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                responce = self.authorized_client.get(address)
                self.assertTemplateUsed(responce, template)
