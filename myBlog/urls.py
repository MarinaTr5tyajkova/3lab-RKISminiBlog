from django.urls import path
from .views import IndexView, RegisterView, LoginView, ProfileView, EditProfileView, CreatePostView, CustomLogoutView

app_name = 'myBlog'  # Define the app name for namespacing

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # Main page with posts
    path('register/', RegisterView.as_view(), name='register'),  # Registration page
    path('login/', LoginView.as_view(), name='login'),  # Login page
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),  # User profile page
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),  # Edit profile page
    path('create-post/', CreatePostView.as_view(), name='create_post'),  # Create post page
]
