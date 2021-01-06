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
        cls.user = user.objects.create(username='PashaBelov')

        Group.objects.create(
            id=1,
            title='First test group title',
            description='About first test group',
            slug='test_slug_one',
        )

        Group.objects.create(
            id=2,
            title='Second test group title',
            description='About second test group',
            slug='test_slug_two',
        )

        cls.group = Group.objects.get(slug='test_slug_one')

        Post.objects.create(
            id=1,
            text='Test first post',
            author=PostsPagesTests.user,
            group=Group.objects.get(slug='test_slug_one'),
        )

        Post.objects.create(
            id=2,
            text='Test second post',
            author=PostsPagesTests.user,
            group=Group.objects.get(slug='test_slug_two'),
        )

        Post.objects.create(
            id=3,
            text='Test third post',
            author=PostsPagesTests.user,
        )

        cls.post = Post.objects.get(id=1)

        cls.all_posts = Post.objects.all()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)

    def test_pages_uses_correct_template(self):
        """Each view-name uses corresponding template."""
        templates_page_names = {
            'index.html': reverse('index'),
            'posts/new.html': reverse('new'),
            'group.html': reverse('group', kwargs={'slug': 'test_slug_one'}),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Template homepage generated with correct context."""
        response = self.authorized_client.get(reverse('index'))
        expected_post = PostsPagesTests.post
        actual_post = response.context.get('page')[-1]
        self.assertEqual(actual_post, expected_post)

    def test_homepage_show_correct_number_of_posts(self):
        """"Template homepage contain all generated posts."""
        response = self.authorized_client.get(reverse('index'))
        (self.assertEqual(len(response.context['page']),
         len(PostsPagesTests.all_posts)))

    def test_group_page_show_correct_context(self):
        """Template group generated with correct context."""
        response = (self.authorized_client.get(reverse('group',
                    kwargs={'slug': 'test_slug_one'})))
        expected_page_details = {
            PostsPagesTests.post: response.context.get('page')[0],
            PostsPagesTests.group: response.context.get('group'),
        }
        for key, value in expected_page_details.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_group_page_show_correct_number_of_posts(self):
        """"Template for second test group contains only posts that belong
        to second group.
        """
        response = (self.authorized_client.get(reverse('group',
                    kwargs={'slug': 'test_slug_two'})))
        (self.assertEqual(len(response.context['page']),
         len(Group.objects.filter(slug='test_slug_two'))))

    def test_new_page_show_correct_context(self):
        """Template new generated with correct context."""
        response = self.authorized_client.get(reverse('new'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
