import pandas
import sqlite3

from API import import_csv

data = []


def home(request):
    global data

    if request.method == 'POST':
        if hasattr(request.POST, 'delete'):
            sqlite3.connect("db.sqlite")
            data = []
        else:
            try:
                data = pandas.read_csv(request.FILES['file'], sep=";")
                if len(data) == 0:
                    raise Exception("Only header in csv file")
                data = import_csv.csv_to_sqlite(data)
            except pandas.errors.EmptyDataError as e:
                print("Empty file")
                print(format(e))
                data = []
                # bad csv file do something
            except pandas.errors.DtypeWarning as e:
                print("Bad Data")
                print(format(e))
                data = []
            except UnicodeDecodeError as e:
                print("Bad file")
                print(format(e))
                data = []
            except pandas.errors.DatabaseError as e:
                print("Error when writing db.sqlite file")
                print(format(e))
                data = []
            except Exception as e:
                print(format(e))
                data = []
    if len(data) == 0:
        return render(request, 'home.html')
    else:
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
