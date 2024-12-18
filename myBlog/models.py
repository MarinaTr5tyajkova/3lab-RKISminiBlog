from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, unique=True)  # Keep this field
    first_name = models.CharField(max_length=30, verbose_name='Имя', blank=False)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия', blank=False)
    patronymic = models.CharField(max_length=30, verbose_name='Отчество', blank=False)  # Mandatory field
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)  # Default avatar
    information = models.TextField(verbose_name='Информация', blank=True)  # Biography field

    def __str__(self):
        return self.nickname

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.created_at}'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)