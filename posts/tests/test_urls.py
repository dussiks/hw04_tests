from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post


SLUG = 'test_slug'
INDEX_URL = '/'
NEW_URL = '/new/'
GROUP_URL = '/group/test_slug/'

class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_john = get_user_model().objects.create(username='john')
        cls.user_bob = get_user_model().objects.create(username='bob')

        cls.group = Group.objects.create(
            title='Test title',
            description='About group',
            slug=SLUG,
        )

        posts_list = []
        for i in range(1, 15):
            posts_list.append(Post(
                text='Test multiple text ' + str(i),
                author=cls.user_bob,
            ))
        Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client_bob = Client()
        self.auth_client_bob.force_login(PostsURLTests.user_bob)
        self.auth_client_john = Client()
        self.auth_client_john.force_login(PostsURLTests.user_john)
        self.url_dict = {
            'profile_url': '/bob/',
            'post_url': '/bob/14/',
            'post_edit_url': '/bob/14/edit/',
        }

    def test_urls_uses_correct_template(self):
        """URL-address uses corresponding template."""
        templates_url_names = {
            INDEX_URL: 'index.html',
            NEW_URL: 'posts/new.html',
            GROUP_URL: 'group.html',
            self.url_dict['profile_url']: 'profile.html',
            self.url_dict['post_url']: 'post.html',
            self.url_dict['post_edit_url']: 'posts/new.html',
            }
        for url_name, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.auth_client_bob.get(url_name)
                self.assertTemplateUsed(response, template)

    def test_unauthorized_user_permited_urls(self):
        """Certain URL-addresses are permited for unauthorized user."""
        templates_url_names = {
            INDEX_URL: 200,
            NEW_URL: 302,
            GROUP_URL: 200,
            self.url_dict['profile_url']: 200,
            self.url_dict['post_url']: 200,
            self.url_dict['post_edit_url']: 302,
            }
        for url_name, value in templates_url_names.items():
            with self.subTest(value=value):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, value,)

    def test_authorized_user_and_post_author_permited_urls(self):
        """Certain URL-addresses are permited for authorized user
        who is post author.
        """
        templates_url_names = {
            INDEX_URL: 200,
            NEW_URL: 200,
            GROUP_URL: 200,
            self.url_dict['profile_url']: 200,
            self.url_dict['post_url']: 200,
            self.url_dict['post_edit_url']: 200,
            }
        for url_name, value in templates_url_names.items():
            with self.subTest(url_name=url_name):
                response = self.auth_client_bob.get(url_name)
                self.assertEqual(response.status_code, value)

    def test_post_edit_url_not_permitted_for_authorized_user_not_author(self):
        """URL-address /bob/14/edit/ is not permitted for authorized user
        but not post author.
        """
        test_url = self.url_dict['post_edit_url']
        response = self.auth_client_john.get(test_url)
        self.assertEqual(response.status_code, 302)

    def test_new_url_redirect_anonymous_user(self):
        """
        After calling /new/ page by unauthorized user he is redirected to
        authorization page /login/.
        """
        response = self.guest_client.get(NEW_URL, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit_url_redirect_anonymous_user(self):
        """After calling url for post edit by unauthorized user he is
        redirected to post viewing page.
        """
        test_url = self.url_dict['post_edit_url']
        response = self.guest_client.get(test_url, follow=True)
        self.assertRedirects(response, '/bob/14/')

    def test_post_edit_url_redirect_authorized_user_not_author(self):
        """After calling url for post edit by authorized but not
        post author user he is redirected to post viewing page.
        """
        test_url = self.url_dict['post_edit_url']
        response = self.auth_client_john.get(test_url, follow=True)
        self.assertRedirects(response, '/bob/14/')
