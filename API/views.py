from datetime import datetime
from io import BytesIO
import os
from django.http import HttpResponse
import pandas
import sqlite3
from django import forms
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import pandas as pd

from API import import_csv
from API import export

data = []


def home(request):
    global data

    if request.method == 'POST':
        if request.POST.get("delete") == "true":
            conn = sqlite3.connect("db.sqlite")
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS csv_data")
            cur.execute("CREATE TABLE IF NOT EXISTS csv_data(temp integer);")
            conn.close()
            data = []
        elif request.POST.get("export_home") == "true":
            export.make_csv()
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

def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'db.sqlite')
    return sqlite3.connect(db_path)

def generate_graph_age(request):
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]
    df = pd.read_sql_query('SELECT "Date de naissance" FROM '+str(table_name), connection)
    df = df.copy()

    #calculate age of each person
    today_str = datetime.today().strftime('%d%m%y')
    today = pd.to_datetime(today_str, format='%d%m%y')
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], format='%d/%m/%Y')
    df['Age'] = df['Date de naissance'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))
    
    bins = [0, 6, 15.25, float('inf')]
    labels = ['Younger than 6', '6 to 15 years and 3 months', 'Adult']
    
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True, include_lowest=True)
    df['Age Group'] = pd.Categorical(df['Age Group'], categories=labels, ordered=True)

    age_group_counts = df['Age Group'].value_counts().sort_index()

    plt.figure(figsize=(8, 8))
    plt.pie(age_group_counts, labels=age_group_counts.index, autopct='%1.1f%%')
    plt.title('Age Group')
    plt.axis('equal')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

    
    """
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 30, 40, 50]

    # Generate the plot
    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Dummy Graph')

    # Save the plot to a BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Return the image as an HTTP response
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='image/png')
    """


from django.shortcuts import render

# Create your views here.
