from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile, Post, Comment
from .forms import UserRegistrationForm, UserProfileForm, PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.views import LogoutView
from django.db.models import Count


# Представление для главной страницы, отображающей все посты
class IndexView(View):
    def get(self, request):
        # Получаем все посты, отсортированные по дате создания (от новых к старым)
        posts_list = Post.objects.all().order_by('-created_at')
        # Аннотируем посты количеством лайков (комментариев)
        posts_with_like_count = posts_list.annotate(like_count=Count('comments__likes'))
        # Пагинируем посты, показывая по 10 на странице
        paginator = Paginator(posts_with_like_count, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # Отображаем шаблон главной страницы с пагинированными постами
        return render(request, 'myBlog/index.html', {'page_obj': page_obj})


# Представление для регистрации пользователя
class RegisterView(View):
    def get(self, request):
        # Отображаем форму регистрации
        form = UserRegistrationForm()
        return render(request, 'myBlog/register.html', {'form': form})

    def post(self, request):
        # Обработка отправки формы регистрации
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Сохраняем нового пользователя
            return redirect('myBlog:login')  # Перенаправляем на страницу входа
        return render(request, 'myBlog/register.html', {'form': form})  # Возвращаем форму с ошибками


# Представление для входа пользователя
class LoginView(View):
    def get(self, request):
        # Отображаем форму входа
        form = AuthenticationForm()
        return render(request, 'myBlog/login.html', {'form': form})

    def post(self, request):
        # Обработка отправки формы входа
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)  # Аутентификация пользователя
            if user is not None:
                login(request, user)  # Входим в систему как пользователь
                return redirect('myBlog:index')  # Перенаправляем на главную страницу
        return render(request, 'myBlog/login.html', {'form': form})  # Возвращаем форму с ошибками


# Представление для отображения профиля пользователя и его постов
class ProfileView(View):
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)  # Получаем профиль пользователя или 404 если не найдено
        posts = Post.objects.filter(author=request.user).order_by('-created_at')  # Получаем посты пользователя
        return render(request, 'myBlog/profile.html', {'profile': profile, 'posts': posts})


# Представление для редактирования профиля пользователя
class EditProfileView(View):
    def get(self, request):
        form = UserProfileForm(instance=request.user.profile)  # Заполняем форму текущими данными профиля
        return render(request, 'myBlog/edit_profile.html', {'form': form})

    def post(self, request):
        if 'delete_profile' in request.POST:
            self.delete_profile(request)  # Обработка удаления профиля если это запрашивается
            return redirect('myBlog:index')
        else:
            form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid():
                form.save()  # Сохраняем обновленные данные профиля
                return redirect('myBlog:profile')  # Перенаправляем на страницу профиля
            return render(request, 'myBlog/edit_profile.html', {'form': form})  # Возвращаем форму с ошибками

    def delete_profile(self, request):
        profile = request.user.profile  # Получаем профиль пользователя
        user = request.user

        keep_posts = request.POST.get('keep_posts', False)  # Проверяем нужно ли сохранить посты

        if keep_posts:
            # Если нужно сохранить посты, устанавливаем авторство на None для всех постов пользователя перед удалением аккаунта.
            posts = user.post_set.all()
            for post in posts:
                post.author = None  # Опционально можно установить на какого-то дефолтного пользователя.
                post.save()
            user.delete()  # Удаляем аккаунт пользователя.
        else:
            user.delete()  # Удаляем пользователя и связанные данные.

        return redirect('myBlog:index')


# Представление для создания нового поста
class CreatePostView(View):
    def get(self, request):
        form = PostForm()  # Отображаем пустую форму создания поста.
        return render(request, 'myBlog/create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # Создаем экземпляр поста без сохранения пока.
            post.author = request.user  # Устанавливаем текущего пользователя как автора.
            post.save()  # Сохраняем новый пост.
            return redirect('myBlog:index')  # Перенаправляем на главную страницу.
        return render(request, 'myBlog/create_post.html', {'form': form})  # Возвращаем с ошибками


# Представление для отображения одного поста и его комментариев
class PostDetailView(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post.objects.prefetch_related('comments'), id=post_id)
        comments = Comment.objects.filter(post=post).order_by('-created_at')  # Получаем комментарии к этому посту.
        comment_form = CommentForm()  # Форма для добавления нового комментария.

        return render(request, 'myBlog/post_detail.html', {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        })

    def post(self, request, post_id):
        post = get_object_or_404(Post.objects.prefetch_related('comments'), id=post_id)

        comment_form = CommentForm(request.POST)  # Получаем данные из формы комментария.

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('myBlog:post_detail', post_id=post.id)

        comments = Comment.objects.filter(post=post).order_by('-created_at')

        return render(request, 'myBlog/post_detail.html', {
            'post': post,
            'comments': comments,
            'comment_form': comment_form,
        })


# Представление для редактирования комментария
class EditCommentView(View):
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

        return render(request, 'myBlog/edit_comment.html', {'form': form})


# Представление для удаления комментария
class DeleteCommentView(View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment.objects.select_related('author'), id=comment_id)

        if comment.author != request.user:
            return redirect('myBlog:index')

        post_id = comment.post.id

        if comment.author is None or comment.author == request.user:
            comment.delete()

        else:
            comment.author = None
            comment.save()

        return redirect('myBlog:post_detail', post_id=post_id)


# Представление для лайков/дизлайков комментариев
class LikeCommentView(View):
    def post(self, request, comment_id):
        # Логика лайков/дизлайков комментариев остается без изменений.
        comment = get_object_or_404(Comment.objects.prefetch_related('likes'), id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)

        return redirect('myBlog:post_detail', post_id=comment.post.id)


# Кастомное представление для выхода из системы с перенаправлением на главную страницу после выхода
class CustomLogoutView(LogoutView):
    next_page = 'myBlog:index'


# Представление для редактирования блога
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


# Представление для удаления блога
class DeletePostView(View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return redirect('myBlog:index')
        post.delete()
        return redirect('myBlog:index')
