from posts.tests.test_urls import PostsURLTests
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model()
        cls.user_john = user.objects.create(username='john')
        cls.user_bob = user.objects.create(username='bob')

        Group.objects.create(
            id=1,
            title="First test group title",
            description='About first test group',
            slug='test_slug_one',
        )

        Group.objects.create(
            id=2,
            title="Second test group title",
            description='About second test group',
            slug='test_slug_two',
        )

        cls.group = Group.objects.get(slug='test_slug_one')

        for i in range(1, 15):
            Post.objects.create(
                text='Test post ' + str(i) + ' number',
                author=cls.user_bob,
        )

        Post.objects.create(
            id=31,
            text='Test john first post',
            author=cls.user_john,
            group=Group.objects.get(slug='test_slug_two'),
        )

        Post.objects.create(
            id=32,
            text='Test john second post',
            author=cls.user_john,
            group=Group.objects.get(slug='test_slug_two'),
        )

        Post.objects.create(
            id=33,
            text='Test bob uniq post',
            author=cls.user_bob,
            group=Group.objects.get(slug='test_slug_one'),
        )

        cls.post = Post.objects.get(id=33)

        cls.all_posts = Post.objects.all()

        cls.posts_quantity = cls.user_bob.posts.count()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_bob = Client()
        self.authorized_client_bob.force_login(PostsPagesTests.user_bob)
        self.authorized_client_john = Client()
        self.authorized_client_john.force_login(PostsPagesTests.user_john)

    def test_pages_uses_correct_template(self):
        """Each view-name uses corresponding template."""
        templates_page_names = {
            'index.html': reverse('index'),
            'posts/new.html': reverse('new'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug_one'}),
            'profile.html': reverse('profile', kwargs={'username': 'bob'}),
            'post.html': (reverse('post',
                          kwargs={'username': 'bob', 'post_id': 33})),
            'posts/new.html': (reverse('post_edit',
                               kwargs={'username': 'bob', 'post_id': 33})),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_bob.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Template homepage generated with correct context."""
        response = self.authorized_client_bob.get(reverse('index'))
        expected_post = PostsPagesTests.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_profile_show_correct_context(self):
        """Template profile generated with correct context."""
        response = (self.authorized_client_bob.get(reverse(
                    'profile', args=['bob'],)))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('page')[0],
            PostsPagesTests.posts_quantity: (
                response.context.get('posts_quantity')),
            PostsPagesTests.user_bob: response.context.get('username'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_group_page_show_correct_context(self):
        """Template group generated with correct context."""
        response = (self.authorized_client_bob.get(reverse('group',
                    kwargs={'slug': 'test_slug_one'})))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('page')[0],
            PostsPagesTests.group: response.context.get('group'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_new_page_show_correct_context(self):
        """Template new generated with correct context."""
        response = self.authorized_client_bob.get(reverse('new'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_pattern = response.context.get('is_edit')
        self.assertEqual(edit_pattern, False)

    def test_post_edit_show_correct_context(self):
        """Template post_edit generated with correct context."""
        response = (self.authorized_client_bob.get(reverse('post_edit',
                    args=['bob', 33])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        edit_pattern = response.context.get('is_edit')
        self.assertEqual(edit_pattern, True)

    def test_post_show_correct_context(self):
        """"Template post generated with correct context."""
        response = (self.authorized_client_john.get(reverse('post',
                    kwargs={'username': 'bob', 'post_id': 33})))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('post'),
            PostsPagesTests.posts_quantity: (
                response.context.get('posts_quantity')),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_homepage_show_correct_number_of_posts(self):
        """"Template homepage contains last 10 generated posts."""
        response = self.authorized_client_bob.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 10)

    def test_group_page_show_correct_number_of_posts(self):
        """"Template for first test group contains only posts that belong
        to first group.
        """
        response = (self.authorized_client_john.get(reverse('group',
                    kwargs={'slug': 'test_slug_one'})))
        (self.assertEqual(len(response.context['page']),
         len(Group.objects.filter(slug='test_slug_one'))))
