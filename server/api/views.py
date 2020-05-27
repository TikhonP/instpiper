from django.shortcuts import render
from django.http import JsonResponse
from .models import Token, Req, Proxy
from secrets import token_hex
import json
from django.views.decorators.csrf import csrf_exempt


with open('../config.json', 'r') as f:
    validtokens = json.load(f)['private_tokens']

columns = ["gender", "username", "id_some_num", "race"]

@csrf_exempt
def CreateRecRequest(request):
    if request.method == 'POST':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.GET.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t) == 0:
            return JsonResponse({'status': 0, 'error': 'Invalid token, got {}'.format(token)})
        data = request.body.decode('utf-8')
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'status': 0, 'error': 'Invalid JSON'})
        task = token_hex(20)
        try:
            proxy = Proxy.objects.filter(author=t[0].author, proxy=data['proxy'])
            if len(proxy)==0:
                proxy = Proxy(author=t[0].author, proxy=data['proxy'])
                proxy.save()
            else:
                proxy = proxy[0]
            r = Req(author=t[0].author, token=t[0], data=data['data'], proxy=proxy, is_id=data['is_id'], task=task)
        except KeyError as e:
            return JsonResponse({'status': 0, 'error': 'Invalid data, there is not key {}'.format(e)})
        r.save()

        return JsonResponse({'status': 1, 'task': task})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be POST.'.format(request.method)})


@csrf_exempt
def privateapi(request):
    """controls tasks for reqognition."""

    if 'token' not in request.GET:
        return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
    if request.GET.get('token', '') not in validtokens:
        return JsonResponse({'status': 0, 'error': 'Invalid token'})

    if request.method == 'GET':
        r = Req.objects.filter(is_done=0)
        if len(r) == 0:
            return JsonResponse({'status': 1, 'data': 0})

        response = []
        for i in r:
            response.append({'task': i.task, 'data': i.data, 'proxy': i.proxy.proxy, 'is_id': i.is_id})

        return JsonResponse({'status': 1, 'data': response})
    elif request.method == 'POST':
        data = json.loads(request.body)

        r = Req.objects.get(task=data['task'])
        r.response = data['data']
        r.is_done = 100
        r.save()
        return JsonResponse({'status': 1})
    elif request.method == 'PUT':
        data = json.loads(request.body)

        r = Req.objects.get(task=data['task'])
        if r.is_done == 100:
            return JsonResponse({'status': 0, 'error': 'Task already done'})
        elif data['is_done'] not in range(1, 101):
            return JsonResponse({'status': 0, 'error': 'IS_DONE is out of range. Must be from 1 to 100, but got {}'.format(data['is_done'])})
        r.is_done = int(data['is_done'])
        out = ""
        for i in json.loads(data['data']):
            for j in i:
                out += j+","
            out = out[:-1]+"\n"
        if r.response is None:
            oout = ""
            for i in columns:
                oout += i+","
            out = oout[:-1]+"\n"+out
            r.response = out
        else:
            r.response += out
        r.save()
        return JsonResponse({'status': 1})
    else:
        return JsonResponse({'status': 0, 'error': 'Invalid request method ({}). Must be GET, POST or PUT.'.format(request.method)})


@csrf_exempt
def CheckComplite(request):
    if request.method == 'GET':
        if 'token' not in request.GET:
            return JsonResponse({'status': 0, 'error': 'Did not get TOKEN argument, you must add token'})
        token = request.GET.get('token', '')
        t = Token.objects.filter(token=token, is_valid=True)
        if len(t) == 0:
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
        if len(t) == 0:
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
