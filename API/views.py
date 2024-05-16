from API import import_csv
import pandas
data = []


def home(request):
    global data

    if request.method == 'POST':
        data = pandas.read_csv(request.FILES['file'], sep=";")
        data = import_csv.csv_to_sqlite(data)
        return render(request, 'home.html', {'data': data})
    else:
        return render(request, 'home.html')



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
