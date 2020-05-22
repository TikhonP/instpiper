from django.shortcuts import render


def privacy(request):
    if request.method == 'GET':
        return render(request, 'privacy.html')
