from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'created_at')  # Display author_name instead of author
    search_fields = ('title', 'content')  # Enable search functionality for these fields
    list_filter = ('author',)  # Allow filtering by author

admin.site.register(Post, PostAdmin)

