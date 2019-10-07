from flask import Flask, render_template, request
import json
import pyodbc 


settings = None

app = Flask(__name__)

class Item(object):
    def __init__(self, name, type, server, description):
        self.name = name
        self.type = type
        self.server = server
        self.description = description

# Or, equivalently, some dicts
items = [dict(name='Name1', type='Type', server='Server', description='Description1'),
         dict(name='Name2', type='Type', server='Server', description='Description2'),
         dict(name='Name3', type='Type', server='Server', description='Description3')]

columns = ["name", "type", "server", "description"]
sql_cols = ('name', 'type_desc', )
types = ('U', 'V', 'P', )

def getItemsFromSQL():
    for database in settings["databases"]:
        connection_string = database # Databases are stored in Connection String form.
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME")
        servername = cursor.fetchone()[0]
        cursor.execute('SELECT ? FROM sys.objects ?', (sql_cols, types, ))
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

if __name__ == '__main__':
    with open('./settings.json') as settings_file:
        settings = json.loads(settings_file.read())
    app.run()
