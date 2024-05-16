import pandas

from API import import_csv

data = []


def error(e):
    global data
    print(format(e))
    data = []


def home(request):
    global data

    if request.method == 'POST':
        try:
            data = pandas.read_csv(request.FILES['file'], sep=";")
            if len(data) == 0:
                raise Exception("Only header in csv file")
            data = import_csv.csv_to_sqlite(data)
        except pandas.errors.EmptyDataError as e:
            print("Empty file")
            error(e)
            # bad csv file do something
        except pandas.errors.DtypeWarning as e:
            print("Bad Data")
            error(e)
        except UnicodeDecodeError as e:
            print("Bad file")
            error(e)
        except pandas.errors.DatabaseError as e:
            print("Error when writing db.sqlite file")
            error(e)
        except Exception as e:
            error(e)

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
