from API import import_csv

data = []


def home(request):
    global data

    data = import_csv.csv_to_sqlite("API/asset/export_rdv_2023-10-01-2023-12-31.csv")
    return render(request, 'home.html', {'data': data})


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
