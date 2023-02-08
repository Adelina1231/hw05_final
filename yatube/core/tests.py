from django.test import TestCase, Client
from http import HTTPStatus


class CoreViewTest(TestCase):
    @classmethod
    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        """Страница 404 использует соответствующий шаблон."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_unexisting_page_url_exists_at_desired_location(self):
        """"Страница /unexisting_page/ ведёт к ошибке 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
