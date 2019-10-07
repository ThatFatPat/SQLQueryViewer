from flask import Flask, render_template, request
import pyodbc
import json

app = Flask(__name__)
wsgi_app = app.wsgi_app

settings = None
with open('./settings.json') as settings_file:
    settings = json.loads(settings_file.read())

columns = ["name", "type", "server", "description"]


sql_cols = ('name', 'type_desc', )

sql_cols = ','.join(map(str, sql_cols)) # Join sql-cols to a comma-seperated string.


types = ('U', 'V', 'P', )

types = "',N'".join(map(str, types)) # Join types to a comma-seperated string.
types = "(N'" + types + "')"
# Output format is "N'U',N'V',N'P'"


def getItemsFromSQL():
    for database in settings["databases"]:
        connection_string = database # Databases are stored in Connection String form.
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME")
        servername = cursor.fetchone()[0]

        # Note: This code is bad form! Please avoid using format strings for queries.
        # Prefer using the builtin paramter method that performs sanitization in order to avoid SQL Injection attacks.
        # In this specific case it proved necessary. This use case is tolerated because the parameters are not user input that has to be sanitized.
        cursor.execute('SELECT {} FROM sys.objects WHERE type IN {}'.format(sql_cols, types))

        rows = cursor.fetchall()
        list_rows = [list(row) for row in rows]
        for row in list_rows:
            row.extend([servername, "Description"])
        dict_rows = [dict(zip(columns, list_row)) for list_row in list_rows]
        conn.close()
        print(dict_rows)
    return dict_rows

@app.route('/')
def displayTable():
    return render_template('index.html', items=getItemsFromSQL())

# if __name__ == '__main__':
#     app.run()