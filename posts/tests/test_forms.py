from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model()
        cls.user = user.objects.create(username='DenSmolov')

        cls.group = Group.objects.create(
            id=1,
            title='First test group title',
            description='About first test group',
            slug='test_slug_one',
        )

        Post.objects.create(
            id=1,
            text='Test first post',
            author=PostCreateFormTests.user,
            group=Group.objects.get(slug='test_slug_one'),
        )

        Post.objects.create(
            id=2,
            text='Test second post',
            author=PostCreateFormTests.user,
        )

        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Valid form create correct post in choosen group."""
        all_posts_count = Post.objects.count()
        group_posts_count = PostCreateFormTests.group.posts.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
            'text': 'Test third post from form',
        }
        response = self.authorized_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), all_posts_count+1)
        self.assertRedirects(response, '/')
        (self.assertEqual(PostCreateFormTests.group.posts.count(),
         group_posts_count+1))


    def test_cant_create_post_without_required_field(self):
        """New post not created if required fields are not filled in form."""
        all_posts_count = Post.objects.count()
        form_data = {
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), all_posts_count)
        self.assertEqual(response.status_code, 200)
