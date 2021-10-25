from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        Post.objects.create(
            author=cls.user,
            text='Текст',
        )
        Group.objects.create(
            title='Заголовок',
            slug='tesg',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Albus')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'tesg'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'Albus'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': (
                reverse('posts:post_create')
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0], Post.objects.all()[0]
        )

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'tesg'})
        )
        group = get_object_or_404(Group, slug='tesg')
        self.assertEqual(response.context['group'], group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Albus'})
        )
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count_posts'], self.user.posts.count()
        )

    def test_post_id_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        self.assertEqual(response.context['post'].pk, Post.objects.get().pk)
        self.assertEqual(
            response.context['count_posts'], Post.objects.all().count()
        )
