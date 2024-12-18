from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views import View
from django.contrib.auth.models import User
from .models import Profile, Post
from .forms import UserRegistrationForm, UserProfileForm, PostForm
from django.core.paginator import Paginator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView


class IndexView(View):
    def get(self, request):
        posts_list = Post.objects.all().order_by('-created_at')  # Получаем все посты
        paginator = Paginator(posts_list, 10)  # Пагинация по 10 постов на страницу

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'myBlog/index.html', {'page_obj': page_obj})

class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'myBlog/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            return redirect('myBlog:login')  # Перенаправляем на страницу входа после регистрации

        return render(request, 'myBlog/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'myBlog/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('myBlog:home')  # Перенаправляем на главную страницу после успешного входа
        return render(request, 'myBlog/login.html', {'form': form})


class ProfileView(View):
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)  # Получаем профиль текущего пользователя
        posts = Post.objects.filter(author=request.user).order_by('-created_at')  # Получаем посты текущего пользователя
        return render(request, 'myBlog/profile.html', {'profile': profile, 'posts': posts})

class EditProfileView(View):
    def get(self, request):
        form = UserProfileForm(instance=request.user.profile)
        return render(request, 'myBlog/edit_profile.html', {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('myBlog:profile')  # Перенаправляем на страницу профиля после сохранения
        return render(request, 'myBlog/edit_profile.html', {'form': form})

class CreatePostView(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'myBlog/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Устанавливаем автора поста
            post.save()
            return redirect('myBlog:home')  # Перенаправляем на главную страницу после создания поста
        return render(request, 'myBlog/create_post.html', {'form': form})
