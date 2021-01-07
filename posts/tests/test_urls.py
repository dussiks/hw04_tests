from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model()
        cls.user_john = user.objects.create(username='john')
        cls.user_bob = user.objects.create(username='bob')

        Group.objects.create(
            title='Test title',
            description='About group',
            slug='test_slug',
        )
        cls.group = Group.objects.get(slug='test_slug')

        for i in range(1, 15):
            Post.objects.create(
                text='Test multiple text ' + str(i),
                author=cls.user_bob,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_bob = Client()
        self.authorized_client_bob.force_login(PostsURLTests.user_bob)
        self.authorized_client_john = Client()
        self.authorized_client_john.force_login(PostsURLTests.user_john)
        self.url_dict = {
            'index_url': '/',
            'new_url': '/new/',
            'group_url': '/group/test_slug/',
            'profile_url': '/bob/',
            'post_url': '/bob/14/',
            'post_edit_url': '/bob/14/edit/',
        }

    def test_urls_uses_correct_template(self):
        """URL-address uses corresponding template."""
        templates_url_names = {
            self.url_dict['index_url']: 'index.html',
            self.url_dict['new_url']: 'posts/new.html',
            self.url_dict['group_url']: 'group.html',
            self.url_dict['profile_url']: 'profile.html',
            self.url_dict['post_url']: 'post.html',
            self.url_dict['post_edit_url']: 'posts/new.html',
            }
        for url_name, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_bob.get(url_name)
                self.assertTemplateUsed(response, template)

    def test_unauthorized_user_permited_urls(self):
        """Certain URL-addresses are permited for unauthorized user."""
        templates_url_names = {
            self.url_dict['index_url']: 200,
            self.url_dict['new_url']: 302,
            self.url_dict['group_url']: 200,
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
            self.url_dict['index_url']: 200,
            self.url_dict['new_url']: 200,
            self.url_dict['group_url']: 200,
            self.url_dict['profile_url']: 200,
            self.url_dict['post_url']: 200,
            self.url_dict['post_edit_url']: 200,
            }
        for url_name, value in templates_url_names.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client_bob.get(url_name)
                self.assertEqual(response.status_code, value)

    def test_post_edit_url_not_permitted_for_authorized_user_not_author(self):
        """URL-address /bob/14/edit/ is not permitted for authorized user
        but not post author.
        """
        response = (self.authorized_client_john.get
                    (self.url_dict['post_edit_url']))
        self.assertEqual(response.status_code, 302)

    def test_new_url_redirect_anonymous_user(self):
        """
        After calling /new/ page by unauthorized user he is redirected to
        authorization page /login/.
        """
        response = (self.guest_client.get(self.url_dict['new_url'],
                    follow=True))
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit_url_redirect_anonymous_user(self):
        """After calling /<username>/<post_id>/edit/ page by unauthorized
        user he is redirected to post viewing page /<username>/<post_id>/.
        """
        response = (self.guest_client.get(self.url_dict['post_edit_url'],
                    follow=True))
        self.assertRedirects(response, '/bob/14/')

    def test_post_edit_url_redirect_authorized_user_not_author(self):
        """After calling /<username>/<post_id>/edit/ page by authorized
        but not post author user he is redirected to post viewing page
        /<username>/<post_id>/.
        """
        response = (self.authorized_client_john.get
                    (self.url_dict['post_edit_url'],follow=True))
        self.assertRedirects(response, '/bob/14/')
