from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    if request.method == 'GET':
        return render(request, 'main.html')
    else:
        return HttpResponse("Invalid requsest method ({})".format(request.method))
