from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class PostAboutTest(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница /about/tech/ доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                responce = self.guest_client.get(address)
                self.assertTemplateUsed(responce, template)

    def test_pages_about_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
