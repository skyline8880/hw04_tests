from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Albus')
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        Group.objects.create(
            title='Тестовый заголовок',
            slug='tesg',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index(self):
        response = self.authorized_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        response = self.authorized_client.get('/group/tesg/')
        self.assertEqual(response.status_code, 200)

    def test_profile_username(self):
        response = self.authorized_client.get('/profile/Albus/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id(self):
        response = self.authorized_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_edit(self):
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_anonim_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_anonim_group_slug(self):
        response = self.guest_client.get('/group/tesg/')
        self.assertEqual(response.status_code, 200)

    def test_anonim_profile_username(self):
        response = self.guest_client.get('/profile/Albus/')
        self.assertEqual(response.status_code, 200)

    def test_anonim_posts_post_id(self):
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

    def test_anonim_posts_edit(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/')
        )

    def test_anonim_posts_post_id(self):
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )

    def test_urls_uses_correct_template(self):
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/tesg/': 'posts/group_list.html',
            '/profile/Albus/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in url_names_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
