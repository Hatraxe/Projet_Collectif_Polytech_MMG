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

    plt.figure(figsize=(6, 6))
    plt.pie(age_group_counts, labels=age_group_counts.index, autopct='%1.1f%%')
    plt.title('Age Group', pad=30)
    plt.axis('equal')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

def generate_graph_cree_par(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]
    df = pd.read_sql_query('SELECT "Créé par" FROM '+str(table_name), connection)
    df = df.copy()
    df['Créé par'] = df['Créé par'].str.replace('MMG', '')
    cree_counts = df['Créé par'].value_counts()
    
    
    plt.figure(figsize=(8, 8))
    plt.pie(cree_counts, labels=cree_counts.index, autopct='%1.1f%%')
    plt.title('Créé par', pad=30)
    plt.axis('equal')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')


def generate_graph_RDVs(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
        
    #potential shifts
    colors_potential = []
    colors_covered = []
    potential = []
    unique_dates = df['Date de début'].unique()
    
    for day in unique_dates:
        day_of_week = day.weekday()

        if day_of_week == 5 or day_of_week == 6:
            potential.append(48)
            colors_potential.append('deepskyblue')
            colors_covered.append('blue')
        else:
            potential.append(16)
            colors_potential.append('aquamarine')
            colors_covered.append('mediumseagreen')
        
        
    covered = df.groupby('Date de début')['Début'].count()
        
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, potential, color=colors_potential, label='Potential RDVs')
    plt.bar(unique_dates, covered, color=colors_covered, label='Covered RDVs')
    plt.legend(loc='best')
    plt.grid()
    plt.title("Num RDVs", pad=30)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
    
def generate_graph_RDVs_honored(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')

    taken = []
    absent = []
    unique_dates = df['Date de début'].unique()
    grouped = df.groupby('Date de début')
    
    for date, group in grouped:
        absent_cnt = (group['Statut'] == 'Absent non excusé').sum()
        absent.append(absent_cnt)
        taken_cnt = (group['Statut'] != 'Absent non excusé').sum()
        taken.append(taken_cnt)
        
        
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, taken, color='aquamarine', label='RDVs taken')
    plt.bar(unique_dates, absent, color='mediumseagreen', label='RDVs absent')
    plt.legend(loc='best')
    plt.grid()
    plt.title("Num RDVs honored", pad=30)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
    
       
from django.shortcuts import render

# Create your views here.
