import sqlite3
import tkinter as tk
from tkinter import filedialog

def create_connection(db_file):
    """ create a database connection to the SQLite database
    specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except OSError as e:
        print(e)
    return conn

def select_all_data(conn): # à changer
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM csv_data")
    rows = cur.fetchall()

    return rows

def make_csv():

    db_file = "db.sqlite"
    conn = create_connection(db_file)

    if conn != None:
        rows = select_all_data(conn)

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        try :
            file_path = filedialog.asksaveasfile(filetypes=[("CSV files", "*.csv")],defaultextension="*.csv")
            file_path = file_path.name

            file = open(file_path, 'w')
            titles = "Date de début;Début;Motif du RDV;Notes;Date de saisie;Date de dernière mise à jour;" \
                     "Créé par;Statut;Date de naissance;Heure d'arrivée;Heure de prise en charge;Heure de départ\n"
            file.write(titles)

            for row in rows:
                strRow = ""
                lenRow = len(row) - 1
                for i in range(lenRow):
                    if row[i] == None:
                        str = ""
                    else:
                        str = row[i]
                    if i == lenRow:
                        strRow += str
                    else:
                        strRow += str + ";"
                strRow += "\n"
                file.write(strRow)

            file.close()
        except Exception as e:
            print(format(e))

    conn.close()


