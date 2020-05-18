from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    if request.user.is_authenticated:
        return authed(request)
    else:
        if request.method == 'GET':
            return render(request, 'main.html')
        else:
            return HttpResponse("Invalid requsest method ({})".format(request.method))


def loginp(request):
    pass


def registerp(request):
    pass


def authed(request):
    pass
