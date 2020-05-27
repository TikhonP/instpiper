from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from api.models import Token, Req, Proxy
from secrets import token_hex


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


def removerequest(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'GET':
            req = request.GET.get('req', '')
            r = Req.objects.get(author=request.user, task=req)
            if r is None:
                return HttpResponse('Invalid request token with user not found')
            r.delete()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def removeproxy(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'GET':
            id = request.GET.get('id', '')
            p = Proxy.objects.get(author=request.user, id=id)
            if p is None:
                return HttpResponse('Invalid request token with user not found')
            p.delete()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def renameproxy(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            id = request.POST.get('id', '')
            name = request.POST.get('name', '')
            p = Proxy.objects.get(id=id)
            if p.author != request.user:
                return HttpResponse('Invalid request token with user not found')
            p.name = name
            p.save()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))


def addproxy(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            name = request.POST.get('name', '')
            proxy = request.POST.get('proxy', '')
            print(request.FILES)
            if len(request.FILES) != 0:
                try:
                    proxy = request.FILES['proxyfileinput'].read().decode()
                except UnicodeDecodeError:
                    messages.error(
                        request, 'Неправильный тип файла с прокси, проверьте кодировку и тип. Должен быть текстовый файл в utf-8.')
                    return redirect('/')
            if proxy == '':
                messages.error(
                    request, 'Пустое прокси, добавьте данные и попробуйте еще раз.')
                return redirect('/')
            p = Proxy(author=request.user, proxy=proxy, name=name)
            p.save()
            return redirect('/')
        else:
            return HttpResponse('Invalid requsest method ({}) Must be POST'.format(request.method))


def dounload_csv_output(request):
    if not request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'GET':
            task = request.GET.get('task', '')
            r = Req.objects.get(task=task)
            if r.author != request.user:
                return HttpResponse('Invalid request request with user not found')
            res = r.response
            response = HttpResponse(res, content_type='text/csv charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
                r.task)

            return response
        else:
            return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))
