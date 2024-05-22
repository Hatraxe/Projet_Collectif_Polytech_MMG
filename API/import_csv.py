import sqlite3


def csv_to_sqlite(data):
    data = data.fillna("")  # remove "nan"
    data.drop_duplicates(keep='last')  # remove duplication (when multiple importations)
    data = clear_csv(data)
    database = sqlite3.connect("db.sqlite")
    data.to_sql('csv_data', database, if_exists='append', index=False)
    return data


# Remove unexpect data in csv file like rest (with a filters list)
def clear_csv(data, filters):
    for i in range(len(filters)):
        data = data.drop(data[(data.Notes == filters[i])].index)
    return data

