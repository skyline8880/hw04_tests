import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        cls.posts_count = Post.objects.count()
        cls.group = Group.objects.create(
            slug='tesg'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        form_data = {
            'text': self.post.text,
            'group': self.group.slug or None
        }
        for field, value in form_data.items():
            with self.subTest(field=field, value=value):
                self.authorized_client.post(
                    reverse('posts:post_create'),
                    data=form_data,
                    follow=True
                )
                self.assertEqual(Post.objects.count(), self.posts_count + 1)
                self.assertEqual(form_data.get(field), value)

    def test_edit_post(self):
        self.posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст редактирования',
            'group': self.group or None
        }
        for field, value in form_data.items():
            with self.subTest(field=field, value=value):
                self.authorized_client.post(
                    reverse(
                        'posts:post_edit', kwargs={'post_id': self.post.pk}
                    ),
                    data=form_data,
                    follow=True
                )
                self.post.refresh_from_db()
                self.assertEqual(Post.objects.count(), self.posts_count)
                self.assertEqual(form_data.get(field), value)
