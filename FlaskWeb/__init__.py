from flask import Flask, render_template, request
import logging
from logging import FileHandler
import pyodbc as sql
import hashlib
import json

app = Flask(__name__)

logger = FileHandler('./error.log')
logger.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logger)

try:
    settings = None
    with open('./settings.json') as settings_file:
        settings = json.loads(settings_file.read())
except Exception as e:
    app.logger.error("ERROR While reading and parsing settings.json: {}".format(str(e)))

column_names = ["Name"]
column_names.extend([col["desc"] for col in settings["sql_cols"] + settings["extend_cols"]])

sql_col_names = ["Name"]
sql_col_names.extend([col["desc"] for col in settings["sql_cols"]])

extended_col_names = [col["desc"] for col in settings["extend_cols"]]

name_col_selector = '''CASE 
                            WHEN sys.objects.parent_object_id>0 THEN OBJECT_SCHEMA_NAME(sys.objects.parent_object_id)+ '.'+OBJECT_NAME(sys.objects.parent_object_id)+'.'+sys.objects.name
                            ELSE OBJECT_SCHEMA_NAME(sys.objects.object_id)+'.'+sys.objects.name
                       END
                       AS name'''
sql_cols = name_col_selector
sql_cols = sql_cols + ',' + ','.join(map(str, [col["id"] for col in settings["sql_cols"]])) # Join sql-cols to a comma-seperated string.

extended_cols = settings["extend_cols"]
types = "',N'".join(map(str, settings["object_types"])) # Join types to a comma-seperated string.
types = "(N'" + types + "')" # Output format is "N'U',N'V',N'P'"

def getExtendedProperty(conn, property):
    query = "SELECT " + name_col_selector + ''', value
            FROM sys.extended_properties
            INNER JOIN sys.objects ON sys.extended_properties.major_id=sys.objects.OBJECT_ID AND class=1
            WHERE sys.extended_properties.name = '{}' '''.format(property)
    conn.add_output_converter(-150, lambda x: x.decode('utf-8')) # Handle binary string coming from extended_properties.
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        app.logger.error("ERROR While getting extended properties: {}".format(str(e)))
        raise e

def getItemsFromSQL():
    for i, database in enumerate(settings["databases"]):
        try:
            conn = sql.connect(database)
        except Exception as e:
            app.logger.error("ERROR While connecting to databases[{}]: {}".format(i, str(e)))
            continue
        cursor = conn.cursor()

        # Note: This code is bad form! Please avoid using format strings for queries.
        # Prefer using the builtin paramter method that performs sanitization in order to avoid SQL Injection attacks.
        # In this specific case it proved necessary. This use case is tolerated because the parameters are not user input that has to be sanitized.
        cursor.execute('SELECT {} FROM sys.objects WHERE type IN {} AND is_ms_shipped = 0'.format(sql_cols, types))

        rows = cursor.fetchall()
        dict_rows = [dict(zip(sql_col_names, list(row))) for row in rows]
        extended_property_dicts = [{"col": col["desc"], "dict": dict(getExtendedProperty(conn, col["id"]))} for col in extended_cols]
        for row in dict_rows:
            for prop_dict in extended_property_dicts:
                if row["Name"] in prop_dict["dict"]:
                    row[prop_dict["col"]] = prop_dict["dict"][row["Name"]]
                else:
                    row[prop_dict["col"]] = ""
        conn.close()
    return dict_rows

@app.route('/')
def displayTable():
    return render_template('index.html', items=getItemsFromSQL(), columns=sql_col_names + extended_col_names)

# if __name__ == '__main__':
#     app.run()