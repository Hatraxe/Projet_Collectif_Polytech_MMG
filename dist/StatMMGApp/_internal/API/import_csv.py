import re
import sqlite3
import pandas as pd


def csv_to_sqlite(data):
    """ Put data into sqlite3 database
    :param data: data to be converted in sqlite database
    :return: None
    """
    try:
        database = sqlite3.connect("db.sqlite")
        data.to_sql('csv_data', database, if_exists='replace', index=False)
        database.close()
    except OSError as e:
        print(e)



# Remove unexpect data in csv file like rest
def clear_csv(data):
    """ Remove "nan", \r\n, and space at the end in data
    :param data: data to be cleaned
    :return: data clean
    """
    data = data.fillna("")  # remove "nan"
    # Remove space at the end and \r\n in data #
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'[\r\n]', '', x))
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'\s+$', '', x))
    try:
        rows_to_remove = words_to_remove()
    except:
        rows_to_remove = []

    #data = data[pd.to_datetime(data["Date de naissance"], errors='coerce', dayfirst=True) <= pd.to_datetime('today', dayfirst=True)] # remove born date before today we can't use it for because born date is optional
    save_word_to_remove(rows_to_remove)
    for i in range(len(rows_to_remove)):
        data = data.drop(data[(data.Notes == rows_to_remove[i])].index)
    return data


### file contain a list of word to remove ###
#Save
def save_word_to_remove(words):
    """ save list of words to remove
    in file mot_a_retire.txt at root directory
    :return: None
    """
    filout = open("mot_a_retire.txt", "w")
    for word in words:
        if word != "" or word != "\n":
            filout.write(f"{word}\n")


def words_to_remove():
    """ read list of words to remove
    in file mot_a_retire.txt at root directory
    :return: List of words to remove
    """
    rows_to_remove = []
    filin = open("mot_a_retire.txt", "r")
    lines = filin.readlines()
    for line in lines:
        if line != "\n" and len(line) != 0:
            rows_to_remove.append(line.replace("\n", ""))
    return rows_to_remove
