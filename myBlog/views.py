from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Post
from .forms import UserRegistrationForm, UserProfileForm, PostForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LogoutView


class IndexView(View):
    def get(self, request):
        posts_list = Post.objects.all().order_by('-created_at')
        paginator = Paginator(posts_list, 10)
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
            user = form.save()
            return redirect('myBlog:login')
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
                return redirect('myBlog:index')
        return render(request, 'myBlog/login.html', {'form': form})

class ProfileView(View):
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        return render(request, 'myBlog/profile.html', {'profile': profile, 'posts': posts})

class EditProfileView(View):
    def get(self, request):
        form = UserProfileForm(instance=request.user.profile)
        form.fields['email'].initial = request.user.email
        form.fields['nickname'].initial = request.user.username
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        form.fields['patronymic'].initial = request.user.profile.patronymic
        return render(request, 'myBlog/edit_profile.html', {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save()
            return redirect('myBlog:profile')
        return render(request, 'myBlog/edit_profile.html', {'form': form})

class CreatePostView(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'myBlog/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('myBlog:index')
        return render(request, 'myBlog/create_post.html', {'form': form})

class CustomLogoutView(LogoutView):
    next_page = 'myBlog:index'