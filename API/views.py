import csv
import pandas
from django.http import HttpResponse

from django.shortcuts import render


def home(request):
    global data

    # print(request.POST.get("file"))
    path = 'API/asset/export_rdv_2023-10-01-2023-12-31.csv'
    data = pandas.read_csv(path, sep=";")
    data = data.fillna("") # remove "nan"
    # print(data.fillna(0))
    return render(request, 'home.html', {'data': data})
    # return HttpResponse(data.to_html())

    # if 'data' in vars():
    #     print("OK")
    #     return render(request, 'home.html', {'data': data})
    # else:
    #     return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def graphiques(request):
    return render(request, 'graphiques.html')


def indicators(request):
    return render(request, 'indicators.html')


def dashboard(request):
    return render(request, 'dashboard.html')


from django.shortcuts import render

# Create your views here.
