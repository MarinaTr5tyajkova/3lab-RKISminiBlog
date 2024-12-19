from django.urls import path
from .views import (
    IndexView,
    RegisterView,
    LoginView,
    ProfileView,
    EditProfileView,
    CreatePostView,
    EditPostView,
    DeletePostView,
    PostDetailView,
    EditCommentView,
    DeleteCommentView,
    LikeCommentView,
    CustomLogoutView,
)

app_name = 'myBlog'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),  # Ensure this is correctly defined
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('edit_post/<int:post_id>/', EditPostView.as_view(), name='edit_post'),
    path('delete_post/<int:post_id>/', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('edit_comment/<int:comment_id>/', EditCommentView.as_view(), name='edit_comment'),
    path('delete_comment/<int:comment_id>/', DeleteCommentView.as_view(), name='delete_comment'),
    path('like_comment/<int:comment_id>/', LikeCommentView.as_view(), name='like_comment'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]