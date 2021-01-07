from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model()
        cls.user = user.objects.create(username='pasha')

        cls.group = Group.objects.create(
            id=1,
            title='First test group title',
            description='About first test group',
            slug='test_slug_one',
        )

        Post.objects.create(
            id=1,
            text='Test first post',
            author=PostFormTests.user,
            group=Group.objects.get(slug='test_slug_one'),
        )

        Post.objects.create(
            id=2,
            text='Test second post',
            author=PostFormTests.user,
        )

        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Valid form create correct post in choosen group."""
        all_posts_count = Post.objects.count()
        group_posts_count = PostFormTests.group.posts.count()
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Test third post from form',
        }
        response = self.authorized_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), all_posts_count+1)
        self.assertRedirects(response, '/')
        (self.assertEqual(PostFormTests.group.posts.count(),
         group_posts_count+1))


    def test_cant_create_post_without_required_field(self):
        """New post not created if required fields are not filled in form."""
        all_posts_count = Post.objects.count()
        form_data = {
            'group': PostFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), all_posts_count)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_form_changes_current_post(self):
        """Valid form changes text in post and save it."""
        form_data = {
            'text': 'Edited second post',
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=['pasha', 2]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post', args=['pasha', 2]))
        self.assertContains(response, 'Edited')
