from django.shortcuts import render
from django.http import JsonResponse
from .models import Token, Req
from secrets import token_hex
import json
from django.views.decorators.csrf import csrf_exempt


validtokens = ['123']


@csrf_exempt
def CreateRecRequest(request):
    if request.method == 'POST':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.GET.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t)==0:
            return JsonResponse({'status': 0, 'error': 'Invalid token'})
        data = request.body.decode('utf-8')

        task = token_hex(20)
        r = Req(token=t[0], data=data, task=task)
        r.save()

        return JsonResponse({'status': 1, 'task': task})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be POST.'.format(request.method)})


@csrf_exempt
def privateapi(request):
    ''' controls tasks for reqognition '''

    if 'token' not in request.GET:
        return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
    if request.GET.get('token', '') not in validtokens:
        return JsonResponse({'status': 0, 'error': 'Invalid token'})
    
    if request.method == 'GET':
        r = Req.objects.filter(is_done=False)
        if len(r)==0:
            return JsonResponse({'status': 1, 'data': 0})

        response = []
        for i in r:
            response.append({'task': i.task, 'data': i.data})

        return JsonResponse({'status': 1, 'data': response})
    elif request.method == 'POST':
        data = json.loads(request.body)

        r = Req.objects.get(task=data['task'])
        r.response = data['data']
        r.is_done = True
        r.save()
        
        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be GET or POST.'.format(request.method)})


@csrf_exempt
def CheckComplite(request):
    if request.method == 'GET':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.GET.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t)==0:
            return JsonResponse({'status': 0, 'error': 'Invalid token'})
        
        data = json.loads(request.body)
        r = Req.objects.get(task=data['task'])
        if r is None:
            return JsonResponse({'status': 0, 'error': 'Invalid task id'})
        if r.token != t[0]:
            return JsonResponse({'status': 0, 'error': 'Task id is not valid with token'})
        return JsonResponse({'status': 1, 'task_status': r.is_done})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be GET.'.format(request.method)})


@csrf_exempt
def GetData(request):
    if request.method == 'GET':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.GET.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t)==0:
            return JsonResponse({'status': 0, 'error': 'Invalid token'})
        
        data = json.loads(request.body)
        r = Req.objects.get(task=data['task'])
        if r is None:
            return JsonResponse({'status': 0, 'error': 'Invalid task id'})
        if r.token != t[0]:
            return JsonResponse({'status': 0, 'error': 'Task id is not valid with token'})
        if not r.is_done:
            return JsonResponse({'status': 0, 'error': 'Task is not done'})

        return JsonResponse({'status': 1, 'data': r.response})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be GET.'.format(request.method)})


