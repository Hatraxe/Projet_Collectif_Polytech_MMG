import re
import sqlite3


def csv_to_sqlite(data):
    # data = clear_csv(data)
    database = sqlite3.connect("db.sqlite")
    data.to_sql('csv_data', database, if_exists='replace', index=False)
    # return data





# Remove unexpect data in csv file like rest
def clear_csv(data):
    print(data.Notes)
    data = data.fillna("")  # remove "nan"
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'[\r\n]', '', x)) # en deux regex chatGpt est nul...
    data['Notes'] = data['Notes'].apply(lambda x: re.sub(r'\s+$', '', x))
    #print(data.Notes)
    try:
        rows_to_remove = words_to_remove()
    except:
        rows_to_remove = []
    # print(rows_to_remove)
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
    #print(rows_to_remove)
    return rows_to_remove