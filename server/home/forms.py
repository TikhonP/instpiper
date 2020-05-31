from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import validators


class LoginForm(forms.Form):
    username = forms.CharField(max_length=25, label="Имя пользователя", widget=forms.TextInput(attrs={'placeholder': 'vasek228',  "class": "form-control" }))
    password = forms.CharField(max_length=20, label="Пароль", widget=forms.PasswordInput(attrs={'placeholder': '123321', "class": "form-control" }))


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'placeholder': 'Вася',  "class": "form-control" }))
    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'placeholder': 'Пупкин',  "class": "form-control" }))
    email = forms.CharField(label="Адрес электронной почты", widget=forms.EmailInput(attrs={'placeholder': 'vasa1999@instpiper.com',  "class": "form-control" }))
    username = forms.CharField(label="Имя пользователя", help_text="Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_.", widget=forms.TextInput(attrs={'placeholder': 'vasek228',  "class": "form-control" }))
    password=forms.CharField(max_length=20, label="Придумайте Пароль", help_text="Ваш пароль должен быть длиной 8-20 символов, содержать буквы и цифры, а также не должен содержать пробелов и эмодзи.", widget=forms.PasswordInput(attrs={'placeholder': '123321', "class": "form-control" }), validators=[validate_password])
    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')
    password1 = forms.CharField(max_length=20, label="Введите пароль ещё раз",  widget=forms.PasswordInput(attrs={'placeholder': '123321', "class": "form-control" }))
