from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post
from .models import Comment

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=30, required=True, label='Имя пользователя')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    patronymic = forms.CharField(max_length=30, required=True, label='Отчество')
    avatar = forms.ImageField(required=False, label='Аватар')  # Make sure this field is included

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password1', 'password2', 'first_name', 'last_name', 'patronymic', 'avatar')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['nickname']
        if commit:
            user.save()
            # Create or update the profile with the avatar
            Profile.objects.create(
                user=user,
                nickname=self.cleaned_data['nickname'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                patronymic=self.cleaned_data['patronymic'],
                avatar=self.cleaned_data.get('avatar')  # Save the avatar here if provided
            )
        return user

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Ensure email is included
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
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(username=nickname).exclude(id=self.instance.user.id).exists():
            raise forms.ValidationError("Этот никнейм уже занят.")
        return nickname

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Save email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['nickname']
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']