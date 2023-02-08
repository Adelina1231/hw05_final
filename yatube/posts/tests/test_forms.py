import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus

from posts.forms import PostForm
from posts.models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Petr')
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
            id='1',
            group=cls.group,
            image=uploaded
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self) -> None:
        """Валидная форма создает новый пост."""
        post_count = Post.objects.count()
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif_2,
            content_type='image_2/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded_2,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.last()
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.group, self.group)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self) -> None:
        """Валидная форма редактирует пост и меняет группу."""
        small_gif_3 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_3 = SimpleUploadedFile(
            name='small_3.gif',
            content=small_gif_3,
            content_type='image_3/gif'
        )
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group_2.id,
            'image': uploaded_3,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group, self.group_2)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small_3.gif'
            ).exists()
        )
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        new_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group_2.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0
        )
        self.assertEqual(
            new_group_response.context['page_obj'].paginator.count, 1
        )

    def test_create_comment(self):
        """Валидная форма создает новый комментарий."""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый текст',
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                text='Тестовый текст',
                author=self.user
            )
        )
