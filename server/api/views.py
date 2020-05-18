from django.shortcuts import render
from django.http import JsonResponse
from .models import Token, Req


validtokens = []


def CreateRecRequest(request):
    if request.method == 'POST':
        if 'token' not in request.POST:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.POST.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t)==0:
            return JsonResponse({'status': 0, 'error': 'Invalid token'})
        with open(request.body, 'r') as f:
            data = f.read()

        r = Req(token=t[0], data=data)
        r.save()

        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be POST.'.format(request.method)})


def chackavailable(request):
    if request.method == 'GET':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        if request.GET.get('token', '') not in validtokens:
            return JsonResponse({'status': 0, 'error': 'Invalid token'})



