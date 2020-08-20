from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from api.models import Token, Req, Proxy
from django.contrib import messages
import json
import re
from .forms import LoginForm, RegisterForm, PromoForm
from secrets import token_hex


with open('../config.json', 'r') as f:
    domen = json.load(f)['domen']


def pcheck(a: str) -> str:
    res = [re.search(r'[a-zA-Z]', a), re.search(r'[0-9]', a)]
    if all(res):
        if len(a) in range(8, 21):
            return True
        else:
            return 'Пароль должен быть от 8 до 20 символов.'
    else:
        if len(a) in range(8, 21):
            return ('Слабый пароль. Добавьте ' +
                    'буквы, '*(res[0] is None) +
                    'цифры, '*(res[1] is None) +
                    'и попробуйте еще раз.')
        else:
            return ('Слабый пароль. Пароль должен быть от 8 до 20 символов. Добавьте ' +
                    'буквы, '*(res[0] is None) +
                    'цифры, '*(res[1] is None) +
                    'и попробуйте еще раз.')


def main(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            form = PromoForm()

            return render(request, 'main.html', {'form': form})
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))

def loginp(request):
    if request.user.is_authenticated:
        return authed(request)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    messages.error(request, "Неактивный аккаунт")
            else:
                messages.error(request, 'Неправильный логин или пароль!')
    elif request.method == 'GET':
        form = LoginForm()
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
    return render(request, 'login.html', {'form': form})

def registerp(request):
    if request.user.is_authenticated:
        return authed(request)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['password']!=cd['password1']:
                messages.error(request, 'Пароли не совпадают! Проверьте правильность ввода паролей или придумайте новые.')
            else:
                user = authenticate(username=cd['username'], password=cd['password'])
                if not user:
                    user = form.save()
                    login(request, user)
                    return redirect('/')
                else:
                    messages.error(
                        request, 'Логин уже существует! Придумайте новый, проявите фантазию!')
    elif request.method == 'GET':
        form = RegisterForm()
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))
    return render(request, 'register.html', {'form': form})


def authed(request):
    global domen
    if request.method == 'GET':
        t = Token.objects.filter(author=request.user).order_by('-date')
        len_tokens = len(t)

        r = Req.objects.filter(author=request.user).order_by('-date')
        len_reqs = len(r)

        rt = Token.objects.filter(author=request.user, is_valid=True)
        req_tokens_null = False
        if len(rt) == 0:
            req_tokens_null = True

        p = Proxy.objects.filter(author=request.user).order_by('-date')
        len_proxy = len(p)

        lbp = len(p.filter(health__lt=60))
        params = {
            'user': request.user,
            'tokens': t,
            'len_tokens': len_tokens,
            'req': r,
            'len_reqs': len_reqs,
            'req_tokens': rt,
            'req_tokens_null': req_tokens_null,
            'proxy': p,
            'len_proxy': len_proxy,
            'threads': request.user.profile.availible_threads,
            'domen': domen,
            'avthreads': request.user.profile.threads,
            'len_bad_proxy': lbp,
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


def makerequest(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            token = request.POST['token']
            data = request.POST['data']
            datatype = request.POST.get('datatype', '')
            proxy = request.POST['proxy']
            proxysaved = request.POST.get('proxysaved', '')
            threads = request.POST['threads']
            if threads == '0':
                messages.error(request, 'Количество потоков не может быть равно нулю, поставьте большее количество потоков')
                return redirect('/')
            proxyname = 'Без имени'
            if len(request.FILES) != 0:
                if 'proxyfileinput' in request.FILES:
                    try:
                        proxy = request.FILES['proxyfileinput'].read().decode()
                        proxyname = request.FILES['proxyfileinput'].name
                    except UnicodeDecodeError:
                        messages.error(
                            request, 'Неправильный тип файла с прокси, проверьте кодировку и тип. Должен быть текстовый файл в utf-8.')
                        return redirect('/')
                if 'datafileinput' in request.FILES:
                    try:
                        data = request.FILES['datafileinput'].read().decode()
                    except UnicodeDecodeError:
                        messages.error(
                            request, 'Неправильный тип файла с входными данными, проверьте кодировку и тип. Должен быть текстовый файл в utf-8.')
                        return redirect('/')
            if proxysaved != '' and proxysaved != 'none':
                proxy = Proxy.objects.get(id=proxysaved).proxy
            if datatype == 'usernames':
                is_id = False
            elif datatype == 'ids':
                is_id = True
            else:
                messages.error(
                    request, 'Вы не выбрали тип входных данных, выберите юзернеймы или id.')
                return redirect('/')

            params = {'token': token}
            data = {
                'data': data,
                'is_id': is_id,
                'proxy': proxy,
                'threads': int(threads),
            }

            task = token_hex(20)

            t = Token.objects.get(token=token, is_valid=True)

            if t.author.profile.availible_threads < data['threads']:
                messages.error(
                    request, 'Вы выбрали слишком много потоков ({}), на данный момент доступно {}'.format(data['threads'], t.author.profile.availible_threads))
                return redirect('/')
            proxy = Proxy.objects.filter(
                author=t.author, proxy=data['proxy'])
            if len(proxy) == 0:
                proxy = Proxy(author=t.author, proxy=data['proxy'], name=proxyname)
                proxy.save()
            else:
                proxy = proxy[0]
            r = Req(author=t.author, token=t, data=data['data'],
                    proxy=proxy, is_id=data['is_id'], task=task, threads=data['threads'])
            r.save()

            u = User.objects.get(id=t.author.id)
            u.profile.availible_threads -= data['threads']
            u.save()

            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))


def promo_request(request):
    if request.method == 'POST':
        form = PromoForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data


    else:
        return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))

