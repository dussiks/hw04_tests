from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_static_pages_are_available(self):
        """static_pages are available by their urls."""
        static_pages = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for key, value in static_pages.items():
            with self.subTest(key=key):
                response = self.guest_client.get(key)
                self.assertEqual(response.status_code, value)

    def test_about_static_pages_correct_template(self):
        """static_pages use corresponding template."""
        static_pages_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for page, template in static_pages_urls.items():
            with self.subTest(template=template):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)
