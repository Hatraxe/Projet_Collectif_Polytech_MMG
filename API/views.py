from datetime import date, timedelta, datetime
from dateutil import easter
from io import BytesIO
import os
from django.http import HttpResponse
import sqlite3
from django import forms
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import pandas
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
                    words_to_remove.append(value)
            words_to_remove.append(request.POST.get("add_word"))
            import_csv.save_word_to_remove(words_to_remove)
            if len(raw_data) != 0:
                data = import_csv.clear_csv(raw_data)
                import_csv.csv_to_sqlite(data)

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

def filter_dates(start_date, end_date, df):
    # Filter the DataFrame based on the start and end dates
    if start_date and end_date:
        df = df[(df['Date de début'] >= start_date) & (df['Date de début'] <= end_date)]
    elif start_date:
        df = df[df['Date de début'] >= start_date]
    elif end_date:
        df = df[df['Date de début'] <= end_date]
        
    return df

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
    df = pd.read_sql_query('SELECT * FROM '+str(table_name), connection)
    df = df.copy()

    #EN: Calculate age of each person
    #FR: Calculer l'âge de chaque personne
    today_str = datetime.today().strftime('%d%m%y')
    today = pd.to_datetime(today_str, format='%d%m%y')
    df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], format='%d/%m/%Y')
    df['Age'] = df['Date de naissance'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
    
    
    #EN: Split into 3 age groups
    #FR: Réparti en 3 tranches d'âge
    bins = [0, 6, 15.25, float('inf')]
    labels = ['Moins de 6 ans', 'Moins de 15 ans et 3 mois', 'Adulte']
    
    df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=True, include_lowest=True)
    df['Age Group'] = pd.Categorical(df['Age Group'], categories=labels, ordered=True)

    age_group_counts = df['Age Group'].value_counts().sort_index()

    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(6, 6))
    plt.pie(age_group_counts, labels=age_group_counts.index, autopct='%1.1f%%')
    plt.title('Âge des patients ', pad=30)
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
    df = pd.read_sql_query('SELECT * FROM '+str(table_name), connection)
    df = df.copy()
    df['Créé par'] = df['Créé par'].str.replace('MMG', '')
    df['Créé par'] = df['Créé par'].str.replace('SAMU', 'Médecins régulateurs libéraux')
    df['Date de début'] = pd.to_datetime(df['Date de début'], format='%d/%m/%Y')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
    
    cree_counts = df['Créé par'].value_counts()
    
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(6, 6))
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
#FR: Graphique à barres pour les RDV
def generate_graph_RDV(request):
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
    df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')

    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = df['Date de début'].min()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else: 
        end_date = df['Date de début'].max()
        
    df = filter_dates(start_date, end_date, df)
    
    covered =[]
    made = []
        
    all_dates = pd.to_datetime(df['Date de début'].unique(), format='%d/%m/%Y')
    unique_dates = sorted(all_dates)
    unique_dates = pd.to_datetime(unique_dates, format='%d/%m/%Y')
          
    #EN: Use different color for potential and covered appointments 
    #FR: Utilisez une couleur différente pour les RDV potentiels et couverts
    colors_covered = []
    colors_made = []
    
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
        #FR: Week-end ou jour férié comporte 48 RDV potentiels
        if day_of_week == 5 or day_of_week == 6 or day in holidays:
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
            covered.append(x)
            colors_covered.append('deepskyblue')
            colors_made.append('blue')
        #EN: Work day has 16 potential appointments
        #FR: La journée de travail comporte 16 RDV potentiels
        else:
            covered.append(16)
            colors_covered.append('aquamarine')
            colors_made.append('mediumseagreen')
        
    #EN: Count made appointments in a day
    #FR: Compter les RDV pris dans une journée
    made = df.groupby('Date de début')['Début'].count()
     
        
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, covered, color=colors_covered, label='RDV couverts')
    plt.bar(unique_dates, made, color=colors_made, label='RDV pris')
    plt.legend(loc='best')
    plt.grid()
    plt.title("RDV couverts / RDV pris", pad=30)
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Bar chart for appointments honored/made
#FR: Graphique à barres pour les RDV honorées/pris
def generate_graph_RDV_honored(request):
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
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)

    #EN: Use different color for honored and made appointments 
    #FR: Utilisez une couleur différente pour les RDV pris et honorés
    made = []
    honored = []
    unique_dates = df['Date de début'].unique()
    grouped = df.groupby('Date de début')
    
    #EN: Count honored and made appointments
    #FR: Comptabiliser les RDV honorés et pris
    for date, group in grouped:
        absent_non_excuse_cnt = (group['Statut'] == 'Absent non excusé').sum()
        absent_excuse_cnt = (group['Statut'] == 'Absent excusé').sum()
        absent_cnt = absent_excuse_cnt + absent_non_excuse_cnt
        honored_cnt = group['Début'].count() - absent_cnt
        honored.append(honored_cnt)
        made_cnt = group['Début'].count()
        made.append(made_cnt)
        
    #EN: Make graph 
    #FR: Faire un graphique
    plt.figure(figsize=(20, 10))
    plt.bar(unique_dates, made, color='aquamarine', label='RDV pris')
    plt.bar(unique_dates, honored, color='mediumseagreen', label='RDV honorés')
    plt.legend(loc='best')
    plt.grid()
    plt.title("RDV honorés / RDV pris", pad=30)
    
    #EN: Save graph as a picture
    #FR: Enregistrer le graphique sous forme d'image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

#EN: Generate a table of shifts per month
#FR: Générer un tableau des équipes par mois
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
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'Vacations potentielles', 'Vacations couvertes', 'Pourcentage']
    
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
                
        row = [month, sum(potential[month]), sum(covered[month]), np.round((sum(covered[month])/sum(potential[month])) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')   
    
def generate_indicator_RDV(request):
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
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'RDV potentiels', 'RDV couverts', 'Pourcentage']
    
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
                
        row = [month, sum(potential[month]), sum(covered[month]), np.round((sum(covered[month])/sum(potential[month])) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')   
    
def generate_indicator_RDV_honored(request):
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
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'RDV pris', 'RDV honorés', 'Pourcentage']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    made = {}
    honored = {}
    
    #EN: Count honored and made appointments
    #FR: Comptabiliser les RDV honorés et pris
    for month, group in grouped:
        absent_non_excuse_cnt = (group['Statut'] == 'Absent non excusé').sum()
        absent_excuse_cnt = (group['Statut'] == 'Absent excusé').sum()
        absent_cnt = absent_excuse_cnt + absent_non_excuse_cnt
        honored_cnt = group['Début'].count() - absent_cnt
        honored[month] = honored_cnt
        made[month] = group['Début'].count()
                            
        row = [month, made[month], honored[month], np.round((honored[month]/made[month]) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')

def generate_indicator_distribution_of_RDV(request):
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
    df['Créé par'] = df['Créé par'].str.replace(' MMG', '')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'RDV pris par le 15', 'RDV pris par SAS Ambulatoire', 'RDV pris par SAMU', 'RDV pris par Médecins']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    #EN: Count "Created by" values
    #FR: Comptabiliser "Créé par"
    for month, group in grouped:
        sas_cnt = (group['Créé par'] == 'SAS Ambulatoire').sum()
        samu_cnt = (group['Créé par'] == 'SAMU').sum()
        medecins_cnt = (group['Créé par'] == 'Médecins').sum()
        urgence_cnt = (group['Créé par'] == 'Urgence 1').sum()
        
        total = group['Créé par'].count()
                            
        row = [month, np.round((urgence_cnt/total) * 100, 2), np.round((sas_cnt/total) * 100, 2),
               np.round((samu_cnt/total) * 100, 2), np.round((medecins_cnt/total) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')

def generate_indicator_statut(request):
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
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'Vu', 'À venir', 'Absent excusé', 'Absent non excusé']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    #EN: Count statuses
    #FR: Comptabiliser Statut
    for month, group in grouped:
        vu_cnt = (group['Statut'] == 'Vu').sum()
        avenir_cnt = (group['Statut'] == 'À venir').sum()
        excuse_cnt = (group['Statut'] == 'Absent excusé').sum()
        nonexcuse_cnt = (group['Statut'] == 'Absent non excusé').sum()
        
        total = group['Statut'].count()
                            
        row = [month, np.round((vu_cnt/total) * 100, 2), np.round((avenir_cnt/total) * 100, 2),
               np.round((excuse_cnt/total) * 100, 2), np.round((nonexcuse_cnt/total) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')

def generate_indicator_RDV_made_covered(request):
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
    df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois', 'RDV pris', 'RDV couverts', 'Pourcentage']
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    made = {}
    covered = {}
    
    for month, group in grouped:
        covered[month] = []
        made[month] = group['Début'].count()
        
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
        
        #EN: Weekend or public holiday has 48 potential appointments
        #FR: Week-end ou jour férié comporte 48 RDV potentiels
        for day in month_range:
            if day not in missing:
                day_of_week = day.weekday()
                if day_of_week == 5 or day_of_week == 6 or day in holidays:
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
                
        row = [month, made[month], sum(covered[month]), np.round(made[month]/sum(covered[month]) * 100, 2)]
        table.add_row(row)
        
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')

#EN: Breakdown of times for workdays only
#FR: Découpage des horaires pour les jours ouvrés uniquement
def generate_indicator_breakdown_of_times_workday(request):
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
    df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
    
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    all_hours = list(range(20, 24))
    table = PrettyTable()
    table.field_names = ['Mois'] + [f'{hour}h' for hour in all_hours]
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    for month, group in grouped:
        #EN: dictionary with counters for each hour
        #FR: dictionnaire avec compteurs pour chaque heure
        times = {hour: 0 for hour in all_hours}
        total = 0
        
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
        
        for day in month_range:
            if day not in missing:
                day_of_week = day.weekday()
                if day_of_week != 5 and day_of_week != 6 and day not in holidays:
                    day_group = df[df['Date de début'] == day]
                    
                    #EN: Increase the counter if there is a Debut at that hour
                    #FR: Augmenter le compteur s'il y a un début à cette heure
                    hour = day_group['Début'].dt.hour
                    for h in hour:
                        times[h] = times.get(h, 0) + 1
                        total = total + 1

        #EN: insert row with percentages
        #FR: insérer une ligne avec des pourcentages
        row = [month]
        for key in sorted(times.keys()):
            value = times[key]
            if total != 0:
                percentage = np.round((value / total * 100), 2)
            else:
                percentage = np.round(value, 2)
            row.append(percentage)
        table.add_row(row)
                    
                
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')

#EN: Breakdown of times for weekends and holidays 
#FR: Découpage des horaires week-end et jours fériés
def generate_indicator_breakdown_of_times_weekend_holiday(request):
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
    df['Début'] = pd.to_datetime(df['Début'], format='%Hh%M')
    
    #EN: Get start_date and end_date from request (if sent)
    #FR: Récupère start_date et end_date de la requête (si envoyée)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
    df = filter_dates(start_date, end_date, df)
    
    #EN: First pass to collect all possible hours
    #FR: Premier pass pour récupérer toutes les heures possibles
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    all_hours = set()
    for month, group in grouped:
        hours = group['Début'].dt.hour
        all_hours.update(hours)

    all_hours = sorted(all_hours)
        
    #EN: Create a table with desired columns
    #FR: Créer un tableau avec les colonnes souhaitées
    table = PrettyTable()
    table.field_names = ['Mois'] + [f'{hour}h' for hour in all_hours]
    
    df['Month'] = df['Date de début'].dt.to_period('M')
    grouped = df.groupby('Month')
    
    for month, group in grouped:
        #EN: dictionary with counters for each hour
        #FR: dictionnaire avec compteurs pour chaque heure
        times = {hour: 0 for hour in all_hours}
        total = 0
        
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
        
        for day in month_range:
            if day not in missing:
                day_of_week = day.weekday()
                if day_of_week == 5 or day_of_week == 6 or day in holidays:
                    day_group = df[df['Date de début'] == day]
                    
                    #EN: Increase the counter if there is a Debut at that hour
                    #FR: Augmenter le compteur s'il y a un début à cette heure
                    hour = day_group['Début'].dt.hour
                    for h in hour:
                        times[h] = times.get(h, 0) + 1
                        total = total + 1

        #EN: insert row with percentages
        #FR: insérer une ligne avec des pourcentages
        row = [month]
        for key in sorted(times.keys()):
            value = times[key]
            if total != 0:
                percentage = np.round((value / total * 100), 2)
            else:
                percentage = np.round(value, 2)
            row.append(percentage)
        table.add_row(row)
                
    html_table = table.get_html_string()
    return HttpResponse(html_table, content_type='text/html')
    
from django.shortcuts import render
