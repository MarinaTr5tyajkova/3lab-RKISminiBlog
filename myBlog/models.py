from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30, verbose_name='Имя', blank=False)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия', blank=False)
    patronymic = models.CharField(max_length=30, verbose_name='Отчество', blank=False)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)
    information = models.TextField(verbose_name='Информация', blank=True)

    def __str__(self):
        return self.nickname

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    author_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания поста

    def save(self, *args, **kwargs):
        if self.author:
            self.author_name = self.author.username  # Устанавливаем имя автора при сохранении
        else:
            self.author_name = "Удалённый пользователь"  # Если автор не указан, устанавливаем имя по умолчанию
        super().save(*args, **kwargs)  # Вызываем метод сохранения родительского класса

    def __str__(self):
        return f'{self.author.username if self.author else self.author_name} - {self.created_at}'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # Содержимое комментария
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
