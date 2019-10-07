from flask import Flask, render_template, request
 
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

def getItemsFromSQL():
    return items

@app.route('/')
def displayTable():
    return render_template('index.html', items=getItemsFromSQL())