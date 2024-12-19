from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Post, Comment
from .forms import UserRegistrationForm, UserProfileForm, PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LogoutView
from django.db.models import Count


class IndexView(View):
    def get(self, request):
        posts_list = Post.objects.all().order_by('-created_at')
        posts_with_like_count = posts_list.annotate(like_count=Count('comments__likes'))
        paginator = Paginator(posts_with_like_count, 10)
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


class PostDetailView(View):  # Обновленное представление для отображения поста и комментариев
    def get(self, request, post_id):
        post = get_object_or_404(Post.objects.prefetch_related('comments'),
                                 id=post_id)  # Оптимизация выборки комментариев
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        comment_form = CommentForm()  # Форма для добавления комментария

        return render(request, 'myBlog/post_detail.html', {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        })

    def post(self, request, post_id):
        post = get_object_or_404(Post.objects.prefetch_related('comments'), id=post_id)

        comment_form = CommentForm(request.POST)  # Получаем данные из формы комментария

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post  # Привязываем комментарий к посту
            comment.author = request.user  # Устанавливаем автора комментария
            comment.save()
            return redirect('myBlog:post_detail', post_id=post.id)  # Перенаправляем на страницу поста

        comments = Comment.objects.filter(post=post).order_by('-created_at')

        return render(request, 'myBlog/post_detail.html', {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        })


class EditCommentView(View):  # Представление для редактирования комментариев
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment.objects.select_related('author'), id=comment_id)

        if comment.author != request.user:
            return redirect('myBlog:index')

        form = CommentForm(instance=comment)

        return render(request, 'myBlog/edit_comment.html', {'form': form})

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment.objects.select_related('author'), id=comment_id)

        if comment.author != request.user:
            return redirect('myBlog:index')

        form = CommentForm(request.POST)

        if form.is_valid():
            comment.content = form.cleaned_data['content']
            comment.save()

            return redirect('myBlog:post_detail', post_id=comment.post.id)


class DeleteCommentView(View):  # Представление для удаления комментариев
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment.objects.select_related('author'), id=comment_id)

        if comment.author != request.user:
            return redirect('myBlog:index')

        post_id = comment.post.id

        comment.delete()

        return redirect('myBlog:post_detail', post_id=post_id)


class LikeCommentView(View):  # Представление для лайков к комментариям
    def post(self, request, comment_id):
        # Логика лайков остается без изменений
        comment = get_object_or_404(Comment.objects.prefetch_related('likes'), id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)

        return redirect('myBlog:post_detail', post_id=comment.post.id)


class CustomLogoutView(LogoutView):
    next_page = 'myBlog:index'

class EditPostView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return redirect('myBlog:index')
        form = PostForm(instance=post)
        return render(request, 'myBlog/edit_post.html', {'form': form})

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return redirect('myBlog:index')
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('myBlog:post_detail', post_id=post.id)
        return render(request, 'myBlog/edit_post.html', {'form': form})

class DeletePostView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return redirect('myBlog:index')
        post.delete()
        return redirect('myBlog:index')