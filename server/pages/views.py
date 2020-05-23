from django.shortcuts import render
from .models import Page
from django.http import HttpResponse

pages_data = {
    'privacy': ['privacy', 'Конфиденциальность'],
    'docs_api': ['docs_api', 'Api Документация'],
}

def main(request, data):
    if request.method == 'GET':
        page = Page.objects.get(name=data[0])
        if page is None:
            return HttpResponse("No page {} in database".format(data[0]))
        return render(request, 'page.html', {'page': page, 'title': data[1]})
    else:
        return HttpResponse('Invalid requsest method ({}) Must be GET'.format(request.method))


def privacy(request):
    return main(request, pages_data['privacy'])


def docs_api(request):
    return main(request, pages_data['docs_api'])
