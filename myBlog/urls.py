from django.urls import path
from .views import IndexView, RegisterView, LoginView, ProfileView, EditProfileView, CreatePostView
from django.contrib.auth.views import LogoutView

app_name = 'myBlog'

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),  # Убедитесь, что этот путь существует
    path('logout/', LogoutView.as_view(next_page='myBlog:login'), name='logout'),  # Используем встроенный LogoutView
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('create-post/', CreatePostView.as_view(), name='create_post'),
]
