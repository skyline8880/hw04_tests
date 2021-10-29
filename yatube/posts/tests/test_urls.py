from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post

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

    def auth_user_url_correct_status(self):
        url_adress_status = {
            '/': 200,
            '/group/tesg/': 200,
            '/profile/Albus/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 200,
            '/create/': 200,
            '/unexisting_page/': 404,
        }
        for adress, status in url_adress_status.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, status)

    def guest_user_url_correct_status(self):
        url_adress_status = {
            '/': 200,
            '/group/tesg/': 200,
            '/profile/Albus/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/create/': 302,
            '/unexisting_page/': 404,
        }
        for adress, status in url_adress_status.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status)

    def redirect_correct_adress(self):
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        if self.guest_client != Post.author:
            self.assertRedirects(
                response, ('/auth/login/?next=/posts/1/')
            )
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/')
        )
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
