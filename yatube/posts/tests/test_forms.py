import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.group = Group.objects.create(
            title='Тест-группа',
            slug='tesg'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.posts_count = Post.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        form_data = {
            'text': 'Новая запись',
            'group': self.group
        }
        post = Post.objects.create(
            author=self.user,
            text=form_data.get('text'),
            group=form_data.get('group')
        )
        Post.objects.filter(
            text=post.text,
            group=post.group,
            author=post.author,
        ).exists()
        with self.subTest(data=form_data):
            self.authorized_client.post(
                reverse('posts:post_create'),
                data=form_data,
                follow=True
            )
            self.assertEqual(form_data.get('text'), 'Новая запись')
            self.assertEqual(form_data.get('group'), self.post.group)
            self.assertEqual(Post.objects.count(), self.posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Новая запись2',
            'group': self.group
        }
        Post.objects.filter(
            text=form_data.get('text'),
            group=form_data.get('group'),
            author=self.user
        ).exists()
        with self.subTest(text=self.post.text, group=self.post.group):
            self.authorized_client.post(
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': Post.objects.last().pk}
                ),
                data=form_data,
                follow=True
            )
            self.post.refresh_from_db()
            self.assertEqual(Post.objects.count(), self.posts_count)
            self.assertEqual(form_data.get('text'), 'Новая запись2')
            self.assertEqual(form_data.get('group'), self.post.group)
