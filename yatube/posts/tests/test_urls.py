from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id='100',
        )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_exists_at_desired_location(self) -> None:
        """Страница доступна любому пользователю."""
        address_page = (
            '/',
            '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/100/'
        )
        for address in address_page:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_exists_at_desired_location_authorized(self) -> None:
        """Страница доступна авторизованному пользователю."""
        address_page = (
            '/create/',
            '/posts/100/edit/',
            '/follow/'
        )
        for address in address_page:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_id_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/<post_id>/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/posts/100/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/100/edit/'))

    def test_follow_url_redirect_anonymous_on_admin_login(self):
        """Страница /follow/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/follow/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/follow/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/100/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/100/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
