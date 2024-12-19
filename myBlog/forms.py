from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post
from .models import Comment

class UserRegistrationForm(UserCreationForm):
    # Поля для регистрации пользователя
    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=30, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    patronymic = forms.CharField(max_length=30, required=True, label='Отчество')
    avatar = forms.ImageField(required=False, label='Аватар')

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password1', 'password2', 'first_name', 'last_name', 'patronymic', 'avatar')

    def clean_email(self):
        # Валидация поля email
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():  # Проверка на уникальность email
            raise forms.ValidationError('This email address is already associated with an account.')
        return email

    def save(self, commit=True):
        # Сохранение нового пользователя и его профиля
        user = super().save(commit=False)
        user.username = self.cleaned_data['nickname']
        if commit:
            user.save()  # Сохраняем пользователя в БД
            # Создаем или обновляем профиль с аватаром
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data['nickname'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                patronymic=self.cleaned_data['patronymic'],
                avatar=self.cleaned_data.get('avatar')  # Сохраняем аватар, если он был загружен
            )
        return user


class UserProfileForm(forms.ModelForm):
    # Поля для редактирования профиля пользователя
    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=30, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    patronymic = forms.CharField(max_length=30, required=True, label='Отчество')
    avatar = forms.ImageField(required=False, label='Аватар')
    information = forms.CharField(widget=forms.Textarea, required=False, label='Информация')

    class Meta:
        model = Profile
        fields = ['email', 'nickname', 'first_name', 'last_name', 'patronymic', 'avatar', 'information']

    def clean_nickname(self):
        # Валидация поля никнейма на уникальность
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(username=nickname).exclude(id=self.instance.user.id).exists():
            raise forms.ValidationError("Этот никнейм уже занят.")
        return nickname

    def save(self, commit=True):
        # Сохранение изменений в профиле и связанном пользователе
        user = self.instance.user  # Получаем связанный объект User из профиля
        user.email = self.cleaned_data['email']  # Сохраняем новый email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['nickname']

        if commit:
            user.save()  # Сохраняем изменения в User в БД
            self.instance.save()  # Сохраняем изменения в Profile в БД

        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']  # Поля формы (контент поста)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Поля формы (контент комментария)
