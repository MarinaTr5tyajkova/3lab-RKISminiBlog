from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'created_at')
    search_fields = ('title', 'content')  # Включаем возможность поиска по заголовку и содержимому поста
    list_filter = ('author',)  # Позволяем фильтрацию постов по автору


admin.site.register(Post, PostAdmin)


