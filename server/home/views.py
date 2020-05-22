from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from api.models import Token, Req
from secrets import token_hex
import requests


domen = 'http://127.0.0.1:8000' 

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
                return HttpResponse('Invalid username or password')
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
                return HttpResponse('Passwords id not same')
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
                return HttpResponse('Username already exists')
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
        params = {
            'user': request.user,
            'tokens': t,
            'tokens_null': tokens_null,
            'req': r,
            'requests_null': requests_null,
        }
        return render(request, 'authed.html', params)
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
        if request.method == 'GET':
            t = Token(author=request.user, token=token_hex(20))
            t.save()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


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
        if request.method == 'GET':
            t = Token.objects.filter(author=request.user, is_valid=True)
            tokens_null = False
            if len(t) == 0:
                tokens_null = True

            params = {
                'tokens': t,
                'tokens_null': tokens_null,
            }
            return render(request, 'makerequest.html', params)
        elif request.method == 'POST':
            token = request.POST['token']
            data = request.POST['data']
            
            url = '{}/api/createrequest'.format(domen)
            params = {'token': token}
            answer = requests.post(url, params=params, data=data.encode())
            answer = answer.json()
            print(answer)
            if answer['status']:
                return redirect('/')
            else:
                return HttpResponse(answer)
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET or POST'.format(request.method))


