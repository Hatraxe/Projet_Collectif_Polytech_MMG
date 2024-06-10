from datetime import date, timedelta, datetime
from dateutil import easter
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
import numpy as np
from prettytable import PrettyTable


from API import import_csv
from API import export

raw_data = []
data = []

def home(request):
    global data
    global raw_data

    if request.method == 'POST':
        # handle delete button
        if request.POST.get("delete") == "true":
            conn = sqlite3.connect("db.sqlite")
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS csv_data")
            cur.execute("CREATE TABLE IF NOT EXISTS csv_data(temp integer);")
            conn.close()
            data = []

        #handle export button
        elif request.POST.get("export_home") == "true":
            export.make_csv()

        #handle add "word" button
        elif request.POST.get("remove_word") == "true":
            words_to_remove = []
            for key, value in request.POST.items():
                if key.startswith('item') and value:
                    print(value)
                    words_to_remove.append(value)
            print(words_to_remove)
            words_to_remove.append(request.POST.get("add_word"))
            import_csv.save_word_to_remove(words_to_remove)
            if len(raw_data) != 0:
                data = import_csv.clear_csv(raw_data)
                import_csv.csv_to_sqlite(data)
            # print(words_to_remove)

        #handle add file in import button
        else:
            try:
                raw_data = pandas.read_csv(request.FILES['file'], sep=";")
                if len(raw_data) == 0:
                    raise Exception("Only header in csv file")
                data = import_csv.clear_csv(raw_data)
                import_csv.csv_to_sqlite(data)
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
        return render(request, 'home.html', {'rm_list': import_csv.words_to_remove()})
    else:
        return render(request, 'home.html', {'data': data, 'rm_list': import_csv.words_to_remove()})


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

#EN: Get connection to the database
#FR: Obtenir une connexion à la base de données
def get_db_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'db.sqlite')
    return sqlite3.connect(db_path)

#EN: Get public holidays for desired year
#FR: Obtenez les jours fériés pour l'année souhaitée
def get_holidays(year):
    #EN: Fixed date public holidays
    #FR: Jours fériés à date fixe
    holidays = [
        date(year, 1, 1),   # New Year's Day
        date(year, 5, 1),   # Labour Day
        date(year, 5, 8),   # Victory Day
        date(year, 7, 14),  # Bastille Day
        date(year, 8, 15),  # Assomption
        date(year, 11, 1),  # All Saints' Day
        date(year, 11, 11), # Armistice 1918
        date(year, 12, 25), # Christmas
        date(year, 12, 26), # Saint Étienne
    ]
    
    #EN: Calculate Easter Sunday
    #FR: Calculer le dimanche de Pâques
    easter_sunday = easter.easter(year)
    
    #EN: Calculate movable public holidays
    #FR: Calculer les jours fériés mobiles
    good_friday = easter_sunday - timedelta(days=2)
    
    easter_monday = easter_sunday + timedelta(days=1)
    
    ascension_day = easter_sunday + timedelta(days=39)
    
    whit_monday = easter_sunday + timedelta(days=50)
    
    #EN: Add these public holidays to the list
    #FR: Ajouter ces jours fériés à la liste
    holidays.append(good_friday)
    holidays.append(easter_monday)
    holidays.append(ascension_day)
    holidays.append(whit_monday)
    
    return holidays
    
#EN: Pie chart for age groups
#FR: Diagramme circulaire pour les groupes d'âge
def generate_graph_age(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]
    
    #EN: Get date of birth
    #FR: Obtenir la date de naissance
    df = pd.read_sql_query('SELECT "Date de naissance" FROM '+str(table_name), connection)
    df = df.copy()

    #EN: Calculate age of each person
    #FR: Calculer l'âge de chaque personne
    today_str = datetime.today().strftime('%d%m%y')
    today = pd.to_datetime(today_str, format='%d%m%y')
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], format='%d/%m/%Y')
    df['Age'] = df['Date de naissance'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))
    
    #EN: Split into 3 age groups
    #FR: Réparti en 3 tranches d'âge
    bins = [0, 6, 15.25, float('inf')]
    labels = ['Younger than 6', '6 to 15 years and 3 months', 'Adult']
    
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True, include_lowest=True)
    df['Age Group'] = pd.Categorical(df['Age Group'], categories=labels, ordered=True)

    age_group_counts = df['Age Group'].value_counts().sort_index()

    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(6, 6))
    plt.pie(age_group_counts, labels=age_group_counts.index, autopct='%1.1f%%')
    plt.title('Age Group', pad=30)
    plt.axis('equal')
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Pie chart for "created by"
#FR: Diagramme circulaire pour "Créé par"
def generate_graph_cree_par(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]
    
    #EN: Get "Created by" and remove "MMG" from values
    #FR: Obtenez "Créé par" et supprimez "MMG" des valeurs
    df = pd.read_sql_query('SELECT "Créé par" FROM '+str(table_name), connection)
    df = df.copy()
    df['Créé par'] = df['Créé par'].str.replace('MMG', '')
    cree_counts = df['Créé par'].value_counts()
    
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(8, 8))
    plt.pie(cree_counts, labels=cree_counts.index, autopct='%1.1f%%')
    plt.title('Créé par', pad=30)
    plt.axis('equal')
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Bar chart for appointments
#FR: Graphique à barres pour les RDVs
def generate_graph_RDVs(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    #EN: Read data from database
    #FR: Lire les données de la base de données
    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
        
    #EN: Use different color for potential and covered appointments 
    #FR: Utilisez une couleur différente pour les RDVs potentiels et couverts
    colors_potential = []
    colors_covered = []
    potential = []
    unique_dates = df['Date de début'].unique()
    
    #EN: Get the unique years
    #FR: Obtenez les années uniques
    df['Year'] = df['Date de début'].dt.year
    unique_years = df['Year'].unique()
    holidays = []
    
    #EN: For each year, calculate dates of public holidays and put them in a single list 
    #FR: Pour chaque année, calculez les dates des jours fériés et regroupez-les dans une seule liste
    for year in unique_years:
        holidays.extend(get_holidays(year))
        
    for day in unique_dates:
        day_of_week = day.weekday()

        #EN: Weekend or public holiday has 48 potential appointments
        #FR: Week-end ou jour férié comporte 48 RDVs potentiels
        if day_of_week == 5 or day_of_week == 6 or day in holidays:
            potential.append(48)
            colors_potential.append('deepskyblue')
            colors_covered.append('blue')
        #EN: Work day has 16 potential appointments
        #FR: La journée de travail comporte 16 RDVs potentiels
        else:
            potential.append(16)
            colors_potential.append('aquamarine')
            colors_covered.append('mediumseagreen')
        
    #EN: Count covered appointments in a day
    #FR: Compter les RDVs couverts dans une journée
    covered = df.groupby('Date de début')['Début'].count()
        
        
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, potential, color=colors_potential, label='Potential RDVs')
    plt.bar(unique_dates, covered, color=colors_covered, label='Covered RDVs')
    plt.legend(loc='best')
    plt.grid()
    plt.title("Num RDVs", pad=30)
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Bar chart for appointments honored
#FR: Graphique à barres pour les RDVs honorées
def generate_graph_RDVs_honored(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    #EN: Read data from database
    #FR: Lire les données de la base de données
    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')

    #EN: Use different color for taken and absent appointments 
    #FR: Utilisez une couleur différente pour les RDVs pris et absents
    taken = []
    absent = []
    unique_dates = df['Date de début'].unique()
    grouped = df.groupby('Date de début')
    
    #EN: Count absent and non absent appointments
    #FR: Comptabiliser les RDVs absents et non absents
    for date, group in grouped:
        absent_non_excuse_cnt = (group['Statut'] == 'Absent non excusé').sum()
        absent_excuse_cnt = (group['Statut'] == 'Absent excusé').sum()
        absent_cnt = absent_excuse_cnt + absent_non_excuse_cnt
        absent.append(absent_cnt)
        taken_cnt = group['Statut'].count() - absent_cnt
        taken.append(taken_cnt)
        
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, taken, color='aquamarine', label='RDVs taken')
    plt.bar(unique_dates, absent, color='mediumseagreen', label='RDVs absent')
    plt.legend(loc='best')
    plt.grid()
    plt.title("Num RDVs honored", pad=30)
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Generate a table of shifts per month
#FR : Générer un tableau des équipes par mois
def generate_indicator_shifts(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    #EN: Read data from database
    #FR: Lire les données de la base de données
    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Month', 'Potential shifts number', 'Covered shifts number', 'Percentage']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    potential = {}
    covered = {}
    
    for month, group in grouped:
        potential[month] = []
        covered[month] = []
        
        df['Days'] = group['Date de début'].dt.to_period('D')
        df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')

        month_range = pd.date_range(start=month.start_time, end=month.end_time, freq='D')
        missing = month_range.difference(group['Date de début'])
        
        #EN: Get the unique years
        #FR: Obtenez les années uniques
        df['Year'] = df['Date de début'].dt.year
        unique_years = df['Year'].unique()
        holidays = []
        
        #EN: For each year, calculate dates of public holidays and put them in a single list 
        #FR: Pour chaque année, calculez les dates des jours fériés et regroupez-les dans une seule liste
        for year in unique_years:
            holidays.extend(get_holidays(year))
        
        #EN: Weekend or public holiday has 3 potential shifts
        #FR: Week-end ou jour férié comporte 3 équipes potentiels
        for day in month_range:
            if day in missing:
                if day.weekday() == 5 or day.weekday() == 6 or day in holidays:
                    potential[month].append(3)
                else:
                    potential[month].append(1)
            else:
                day_of_week = day.weekday()
                if day_of_week == 5 or day_of_week == 6 or day in holidays:
                    potential[month].append(3)
                    day_group = df[df['Date de début'] == day]
                
                    #EN: x = How many shifts are covered in a non-working day
                    #FR: x = Combien d'équipes sont couvertes dans une journée non ouvrable
                    x = 0 
                    hour = day_group['Début'].dt.hour
                    if (hour >= 12).any() and (hour < 16).any():
                        x += 1
                    if (hour >= 16).any() and (hour < 20).any():
                        x += 1
                    if (hour >= 20).any() and (hour < 24).any():
                        x += 1
                    covered[month].append(x)
                else:
                    covered[month].append(1)
                    potential[month].append(1)
                
        row = [month, sum(potential[month]), sum(covered[month]), np.round(sum(covered[month])/sum(potential[month]), 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')   
    
def generate_indicator_RDVs(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    #EN: Read data from database
    #FR: Lire les données de la base de données
    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Month', 'Potential RDVs number', 'Covered RDVs number', 'Percentage']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    potential = {}
    covered = {}
    
    for month, group in grouped:
        potential[month] = []
        covered[month] = []
        
        df['Days'] = group['Date de début'].dt.to_period('D')
        df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')

        month_range = pd.date_range(start=month.start_time, end=month.end_time, freq='D')
        missing = month_range.difference(group['Date de début'])
        
        #EN: Get the unique years
        #FR: Obtenez les années uniques
        df['Year'] = df['Date de début'].dt.year
        unique_years = df['Year'].unique()
        holidays = []
        
        #EN: For each year, calculate dates of public holidays and put them in a single list 
        #FR: Pour chaque année, calculez les dates des jours fériés et regroupez-les dans une seule liste
        for year in unique_years:
            holidays.extend(get_holidays(year))
        
        #EN: Weekend or public holiday has 3 potential shifts
        #FR: Week-end ou jour férié comporte 3 équipes potentiels
        for day in month_range:
            if day in missing:
                if day.weekday() == 5 or day.weekday() == 6 or day in holidays:
                    potential[month].append(48)
                else:
                    potential[month].append(16)
            else:
                day_of_week = day.weekday()
                if day_of_week == 5 or day_of_week == 6 or day in holidays:
                    potential[month].append(48)
                    day_group = df[df['Date de début'] == day]
                
                    #EN: x = How many shifts are covered in a non-working day
                    #FR: x = Combien d'équipes sont couvertes dans une journée non ouvrable
                    x = 0 
                    hour = day_group['Début'].dt.hour
                    if (hour >= 12).any() and (hour < 16).any():
                        x += 16
                    if (hour >= 16).any() and (hour < 20).any():
                        x += 16
                    if (hour >= 20).any() and (hour < 24).any():
                        x += 16
                    covered[month].append(x)
                else:
                    covered[month].append(16)
                    potential[month].append(16)
                
        row = [month, sum(potential[month]), sum(covered[month]), np.round(sum(covered[month])/sum(potential[month]), 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')   
    
def generate_indicator_RDVs_honored(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_name = tables[0][0]

    #EN: Read data from database
    #FR: Lire les données de la base de données
    df = pd.read_sql_query('SELECT * FROM ' + table_name, connection)
    df = df.copy()
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Month', 'RDVs made number', 'RDVs honored number', 'Percentage']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    made = {}
    honored = {}
    
    #EN: Count absent and non absent appointments
    #FR: Comptabiliser les RDVs absents et non absents
    for month, group in grouped:
        absent_non_excuse_cnt = (group['Statut'] == 'Absent non excusé').sum()
        absent_excuse_cnt = (group['Statut'] == 'Absent excusé').sum()
        absent_cnt = absent_excuse_cnt + absent_non_excuse_cnt
        honored_cnt = group['Statut'].count() - absent_cnt
        honored[month] = honored_cnt
        made[month] = group['Statut'].count()
                            
        row = [month, made[month], honored[month], np.round(honored[month]/made[month], 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')
    
from django.shortcuts import render
