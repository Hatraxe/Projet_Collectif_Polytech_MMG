import re
import sqlite3
import pandas as pd


def csv_to_sqlite(data):
    # data = clear_csv(data)
    database = sqlite3.connect("db.sqlite")
    data.to_sql('csv_data', database, if_exists='replace', index=False)
    # return data





# Remove unexpect data in csv file like rest
def clear_csv(data):
    data = data.fillna("")  # remove "nan"
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'[\r\n]', '', x))
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'\s+$', '', x))
    try:
        rows_to_remove = words_to_remove()
    except:
        rows_to_remove = []

    data = data[pd.to_datetime(data["Date de naissance"], errors='coerce') <= pd.to_datetime('today')]
    save_word_to_remove(rows_to_remove)
    for i in range(len(rows_to_remove)):
        data = data.drop(data[(data.Notes == rows_to_remove[i])].index)
    return data

### file contain a list of word to remove ###
#Save
def save_word_to_remove(words):
    filout = open("mot_a_retire.txt", "w")
    for word in words:
        if word != "" or word != "\n":
            filout.write(f"{word}\n")

def words_to_remove():
    rows_to_remove = []
    filin = open("mot_a_retire.txt", "r")
    lines = filin.readlines()
    for line in lines:
        if line != "\n" and len(line) != 0:
            rows_to_remove.append(line.replace("\n",""))
    return rows_to_remove