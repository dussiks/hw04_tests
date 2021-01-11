from posts.tests.test_urls import PostsURLTests
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


INDEX_URL = reverse('index')
NEW_URL = reverse('new')


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_john = get_user_model().objects.create(username='john')
        cls.user_bob = get_user_model().objects.create(username='bob')

        cls.group = Group.objects.create(
            title="First test group title",
            description='About first test group',
            slug='slug_one',
        )

        Group.objects.create(
            title="Second test group title",
            description='About second test group',
            slug='slug_two',
        )

        posts_list = []
        for i in range(1, 15):
            posts_list.append(Post(
                text='Test post ' + str(i) + ' number',
                author=cls.user_bob,
            ))
        Post.objects.bulk_create(posts_list)

        Post.objects.create(
            id=31,
            text='Test john first post',
            author=cls.user_john,
            group=Group.objects.get(slug='slug_two'),
        )

        Post.objects.create(
            id=32,
            text='Test john second post',
            author=cls.user_john,
            group=Group.objects.get(slug='slug_two'),
        )

        cls.post = Post.objects.create(
            id=33,
            text='Test bob uniq post',
            author=cls.user_bob,
            group=Group.objects.get(slug='slug_one'),
        )

        cls.all_posts = Post.objects.all()

        cls.posts_count = cls.user_bob.posts.count()

    def setUp(self):
        self.guest_client = Client()
        self.auth_client_bob = Client()
        self.auth_client_bob.force_login(PostsPagesTests.user_bob)
        self.auth_client_john = Client()
        self.auth_client_john.force_login(PostsPagesTests.user_john)

    def test_pages_uses_correct_template(self):
        """Each view-name uses corresponding template."""
        templates_page_names = {
            'index.html': INDEX_URL,
            'posts/new.html': NEW_URL,
            'group.html': reverse('group', args=['slug_one']),
            'profile.html': reverse('profile', args=['bob']),
            'post.html': reverse('post', args=['bob', 33]),
            'posts/new.html': reverse('post_edit', args=['bob', 33]),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.auth_client_bob.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Template homepage generated with correct context."""
        response = self.auth_client_bob.get(INDEX_URL)
        expected_post = PostsPagesTests.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_profile_show_correct_context(self):
        """Template profile generated with correct context."""
        response = self.auth_client_bob.get(reverse('profile', args=['bob']))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('page')[0],
            PostsPagesTests.posts_count: response.context.get('posts_count'),
            PostsPagesTests.user_bob: response.context.get('author'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_group_page_show_correct_context(self):
        """Template group generated with correct context."""
        response = self.auth_client_bob.get(reverse('group', args=['slug_one']))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('page')[0],
            PostsPagesTests.group: response.context.get('group'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_new_page_show_correct_context(self):
        """Template new generated with correct context."""
        response = self.auth_client_bob.get(NEW_URL)
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
        post_edit_url = reverse('post_edit', args=['bob', 33])
        response = self.auth_client_bob.get(post_edit_url)
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
        post_url = reverse('post', args=['bob', 33])
        response = self.auth_client_john.get(post_url)
        expected_page_details = {
            PostsPagesTests.post: response.context.get('post'),
            PostsPagesTests.posts_count: response.context.get('posts_count'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_homepage_show_correct_number_of_posts(self):
        """"Template homepage contains last 10 generated posts."""
        response = self.auth_client_bob.get(INDEX_URL)
        self.assertEqual(len(response.context['page']), 10)

    def test_group_page_show_correct_number_of_posts(self):
        """"Template for first test group contains only posts that belong
        to first group.
        """
        group_items = Group.objects.filter(slug='slug_one').count()
        group_url = reverse('group', args=['slug_one'])
        response = self.auth_client_john.get(group_url)
        self.assertEqual(len(response.context['page']), group_items)
