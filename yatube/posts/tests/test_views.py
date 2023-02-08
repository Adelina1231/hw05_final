import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from time import sleep
from django.core.cache import cache

from ..models import Post, Group, Follow, User
from ..forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petr')
        cls.user_following = User.objects.create_user(username='Gleb')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        sleep(0.01)
        cls.post_2 = Post.objects.create(
            author=cls.user_following,
            text='Тестовый пост 2',
            group=cls.group_2
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_following = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_following.force_login(self.user_following)

    def test_pages_uses_correct_template(self) -> None:
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self) -> None:
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        expected = list(Post.objects.select_related('group').all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_page_show_correct_context(self) -> None:
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})))
        expected = list(self.group.posts.all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_page_show_correct_context(self) -> None:
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:profile',
                    kwargs={'username': self.user})))
        expected = list(self.post.author.posts.all())
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_page_show_correct_context(self) -> None:
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.guest_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author, self.post.author)
        self.assertEqual(response.context['post'].group, self.post.group)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_post_create_page_show_correct_context(self) -> None:
        """Шаблон post_create сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_edit_page_show_correct_context(self) -> None:
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_with_group(self):
        """Проверка: пост попадает в нужную группу."""
        self.assertEqual(self.post_2.group.title, 'Тестовая группа 2')
        self.assertEqual(self.post_2.text, 'Тестовый пост 2')

    def test_post_correct_appear(self):
        """Проверка: пост появляется на нужной странице."""
        Follow.objects.create(user=self.user, author=self.user_following)
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}),
            reverse('posts:profile', kwargs={'username': self.user_following}),
            reverse('posts:follow_index')
        }
        for page in page_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.context['page_obj'][0], self.post_2)

    def test_index_page_cache(self) -> None:
        """Страница index/ формируется с использованием кеширования."""
        response = self.guest_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.user,
        )
        response_old = self.guest_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.guest_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_authorized_can_follow(self):
        """Авторизованный пользователь может подписаться и отписаться."""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)
