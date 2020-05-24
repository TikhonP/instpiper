from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from api.models import Token, Req
from secrets import token_hex
import requests
from django.contrib import messages
import json
import re


with open('../config.json', 'r') as f:
    domen = json.load(f)['domen']

def pcheck(a: str) -> str:
    res = [re.search(r"[a-zA-Z]", a), re.search(r"[0-9]", a)]
    if all(res):
        if len(a) in range(8, 21):
            return True
        else:
            return "Пароль должен быть от 8 до 20 символов."
    else:
        if len(a) in range(8, 21):
            return ("Слабый пароль. Добавьте "+
                    "буквы, "*(res[0] is None) +
                    "цифры, "*(res[1] is None) +
                     "и попробуйте еще раз.")
        else:
            return ("Слабый пароль. Пароль должен быть от 8 до 20 символов. Добавьте "+
                    "буквы, "*(res[0] is None) +
                    "цифры, "*(res[1] is None) +
                     "и попробуйте еще раз.")


def main(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            return render(request, 'main.html')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def loginp(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            return render(request, 'login.html')
        elif request.method == 'POST':
            password = request.POST['password']
            username = request.POST['login']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            else:
                messages.error(request, 'Неправильный логин или пароль!')
                return redirect('/login')
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


def registerp(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            return render(request, 'register.html')
        elif request.method == 'POST':
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            username = request.POST['login']
            email = request.POST['email']
            if password1 != password2:
                messages.error(request, 'Пароли не совпадают! Проверьте правильность ввода паролей или придумайте новые.')
                return redirect('/register')
            check = pcheck(password1)
            if type(check)==type(''):
                messages.error(request, check)
                return redirect('/register')
            user = authenticate(username=username, password=password1)
            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    last_name=request.POST['lastName'],
                    first_name=request.POST['firstName']
                )
                user.save()
                login(request, user)
            else:
                messages.error(request, 'Логин уже существует! Придумайте новый, проявите фантазию!')
                return redirect('/login')
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


def authed(request):
    if request.method == 'GET':
        t = Token.objects.filter(author=request.user)
        tokens_null = False
        if len(t) == 0:
            tokens_null = True
        r = Req.objects.filter(author=request.user)
        requests_null = False
        if len(r) == 0:
            requests_null = True

        rt = Token.objects.filter(author=request.user, is_valid=True)
        req_tokens_null = False
        if len(rt) == 0:
           req_tokens_null = True

        params = {
            'user': request.user,
            'tokens': t,
            'tokens_null': tokens_null,
            'req': r,
            'requests_null': requests_null,
            'req_tokens': rt,
            'req_tokens_null': req_tokens_null,
        }
        return render(request, 'authed.html', params)
    elif request.method == 'POST':
        if 'makerequest' in request.POST:
            return makerequest(request)
        elif 'pdatasubm' in request.POST:
            LastName = request.POST.get('LastName', '')
            FirstName = request.POST.get('FirstName', '')
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')

            user = request.user
            user.first_name = FirstName
            user.last_name = LastName
            user.email = email
            user.username = username
            user.save()
            return redirect('/')
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


def logoutp(request):
    if request.method == 'GET':
        logout(request)
        return redirect('/')
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def addtoken(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            name = request.POST.get('name', '')
            t = Token(author=request.user, token=token_hex(20), name=name)
            t.save()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))


def removetoken(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'GET':
            token = request.GET.get('token', '')
            t = Token.objects.get(author=request.user, token=token)
            if t is None:
                return HttpResponse('Invalid request token with user not found')
            t.delete()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def makerequest(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            token = request.POST['token']
            data = request.POST['data']
            print(token)
            if len(request.FILES)!=0:
                try:
                    data = request.FILES['fileinput'].read().decode()
                except UnicodeDecodeError:
                    messages.error(request, 'Непраильный типа файла, проверьте кодировку и тип. Должен быть текстовый файл в utf-8.')
                    return redirect('/')
            url = '{}/api/createrequest'.format(domen)
            params = {'token': token}
            answer = requests.post(url, params=params, data=data.encode())
            answer = answer.json()
            if answer['status']:
                return redirect('/')
            else:
                messages.error(request, 'Ошибка создания запроса {}'.format(answer['error']))
                return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))


