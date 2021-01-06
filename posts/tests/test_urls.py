from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Test title',
            description='About group',
            slug='test_slug',
        )
        cls.group = Group.objects.get(slug='test_slug')

    def setUp(self):
        self.guest_client = Client()
        user = get_user_model()
        self.user = user.objects.create(username='VovaPanov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_dict = {
            'index_url': '/',
            'new_url': '/new/',
            'group_url': '/group/test_slug/',
        }

    def test_urls_uses_correct_template(self):
        """URL-address uses corresponding template."""
        templates_url_names = {
            self.url_dict['index_url']: 'index.html',
            self.url_dict['new_url']: 'posts/new.html',
            self.url_dict['group_url']: 'group.html',
            }
        for url_name, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(response, template)

    def test_unauthorized_user_permited_urls(self):
        """Certain URL-addresses are permited for unauthorized user."""
        templates_url_names = {
            self.url_dict['index_url']: 200,
            self.url_dict['new_url']: 302,
            self.url_dict['group_url']: 200,
            }
        for url_name, value in templates_url_names.items():
            with self.subTest(value=value):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, value,)

    def test_authorized_user_permited_urls(self):
        """Certain URL-addresses are permited for authorized user."""
        templates_url_names = {
            self.url_dict['index_url']: 200,
            self.url_dict['new_url']: 200,
            self.url_dict['group_url']: 200,
            }
        for url_name, value in templates_url_names.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertEqual(response.status_code, value)

    def test_new_url_redirect_anonymous_user(self):
        """
        After calling /new/ page by unauthorized user he is redirected to
        authorization page /login/.
        """
        response = (self.guest_client.get(self.url_dict['new_url'],
                    follow=True))
        self.assertRedirects(response, '/auth/login/?next=/new/')
