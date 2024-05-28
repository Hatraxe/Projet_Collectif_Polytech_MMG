import sqlite3


def csv_to_sqlite(data):

    data = clear_csv(data)
    database = sqlite3.connect("db.sqlite")
    data.to_sql('csv_data', database, if_exists='replace', index=False)
    return data

def words_to_remove():
    filin = open("mot_a_retire.txt", "r")
    rows_to_remove = filin.readlines()
    return rows_to_remove


# Remove unexpect data in csv file like rest
def clear_csv(data):
    data = data.fillna("")  # remove "nan"
    try :
        rows_to_remove = words_to_remove()
    except:
        rows_to_remove = []
    save_word_to_remove(rows_to_remove)
    for i in range(len(rows_to_remove)):
        data = data.drop(data[(data.Notes == rows_to_remove[i])].index)
    return data

def save_word_to_remove(words):
    filout = open("mot_a_retire.txt", "w")
    for word in words:
        filout.write(f"{word}\n")