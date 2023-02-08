from django.db import models
from django.contrib.auth import get_user_model

from yatube.settings import LEN_POST
from core.models import PubDatedModel


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Адрес')
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title

    class Meta():
        verbose_name_plural = 'Группы'


class Post(PubDatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:LEN_POST]

    class Meta():
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите комментарий')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата публикации')

    def __str__(self) -> str:
        return self.text

    class Meta:
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def __str__(self) -> str:
        return f'Подписка {self.user} на {self.author}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_not_self_follow'
            )
        ]
