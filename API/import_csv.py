import pandas
import sqlite3


def csv_to_sqlite(data):
    data = data.fillna("")  # remove "nan"
    data = clear_csv(data)
    database = sqlite3.connect("db.sqlite")
    data.to_sql('csv_data', database, if_exists='replace', index=False)
    return data


def clear_csv(data):
    rows_to_remove = ["P", "pause", "p"]
    for i in range(len(rows_to_remove)):
        data = data.drop(data[(data.Notes == rows_to_remove[i])].index)
    return data

