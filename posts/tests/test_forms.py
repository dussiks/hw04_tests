from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='pasha')

        cls.group = Group.objects.create(
            title='First test group title',
            description='About first test group',
            slug='slug_one',
        )

        Post.objects.create(
            text='Test first post',
            author=PostFormTests.user,
            group=Group.objects.get(slug='slug_one'),
        )

        Post.objects.create(
            text='Test second post',
            author=PostFormTests.user,
        )

        cls.form = PostForm()

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Valid form create correct post in choosen group."""
        all_posts_count = Post.objects.count() 
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Test third post from form',
        }
        response = self.auth_client.post(
            reverse('new'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), all_posts_count+1)
        new_post = Post.objects.get(text__icontains='post from form')
        answer = self.auth_client.get('/group/slug_one/')
        actual_post = answer.context.get('page')[0]
        self.assertEqual(actual_post, new_post)

    def test_cant_create_post_without_required_field(self):
        """New post not created if required fields are not filled in form."""
        all_posts_count = Post.objects.count()
        form_data = {
            'group': PostFormTests.group.id,
        }
        response = self.auth_client.post(
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
        response = self.auth_client.post(
            reverse('post_edit', args=['pasha', 2]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('post', args=['pasha', 2]))
        self.assertContains(response, 'Edited')
