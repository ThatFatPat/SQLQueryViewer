from flask import Flask, render_template, request
import pymssql as sql
import hashlib
import json

app = Flask(__name__)
wsgi_app = app.wsgi_app

settings = None
with open('./settings.json') as settings_file:
    settings = json.loads(settings_file.read())

column_names = [col["desc"] for col in settings["sql_cols"] + settings["extend_cols"]]
sql_col_names = [col["desc"] for col in settings["sql_cols"]]
extended_col_names = [col["desc"] for col in settings["extend_cols"]]
sql_cols = ','.join(map(str, [col["id"] for col in settings["sql_cols"]])) # Join sql-cols to a comma-seperated string.
extended_cols = settings["extend_cols"]
types = "',N'".join(map(str, settings["object_types"])) # Join types to a comma-seperated string.
types = "(N'" + types + "')" # Output format is "N'U',N'V',N'P'"

def getExtendedProperty(cursor, property):
    query = '''SELECT
 CASE WHEN ob.parent_object_id>0 
 THEN OBJECT_SCHEMA_NAME(ob.parent_object_id)
 + '.'+OBJECT_NAME(ob.parent_object_id)+'.'+ob.name 
 ELSE OBJECT_SCHEMA_NAME(ob.object_id)+'.'+ob.name END AS path,
 value
 FROM sys.extended_properties ep
 inner join sys.objects ob ON ep.major_id=ob.OBJECT_ID AND class=1
 WHERE ep.name = '{}'
'''.format(property)
    cursor.execute(query)
    return cursor.fetchall()

def getItemsFromSQL():
    for database in settings["databases"]:
        connection_string = database # Databases are stored in Connection String form.
        #conn = sql.connect(connection_string)
        conn = sql.connect(server="sql5045.site4now.net", database="DB_A4E964_MSSQL", user="DB_A4E964_MSSQL_admin", password="ZP21ya10")
        cursor = conn.cursor()

        # Note: This code is bad form! Please avoid using format strings for queries.
        # Prefer using the builtin paramter method that performs sanitization in order to avoid SQL Injection attacks.
        # In this specific case it proved necessary. This use case is tolerated because the parameters are not user input that has to be sanitized.
        cursor.execute('SELECT {} FROM sys.objects ob WHERE type IN {} AND is_ms_shipped = 0'.format(sql_cols, types))

        rows = cursor.fetchall()
        dict_rows = [dict(zip(sql_col_names, list(row))) for row in rows]
        extended_property_dicts = [{"col": col["desc"], "dict": dict(getExtendedProperty(cursor, col["id"]))} for col in extended_cols]
        for row in dict_rows:
            for prop_dict in extended_property_dicts:
                if row["Name"] in prop_dict["dict"]:
                    row[prop_dict["col"]] = prop_dict["dict"][row["Name"]].decode('utf-8')
                else:
                    row[prop_dict["col"]] = ""
        conn.close()
        print(dict_rows)
    return dict_rows

@app.route('/')
def displayTable():
    return render_template('index.html', items=getItemsFromSQL(), columns=sql_col_names+extended_col_names)

# if __name__ == '__main__':
#     app.run()