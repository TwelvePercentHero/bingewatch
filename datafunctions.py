import os
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

# Database access configuration
app.config['MONGO_DBNAME'] = 'binge_watch'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

""" Filters """

# get_recipes filter
def filter_recipes(form):
    # Filter based on one field returned
    if len(form) == 1:
        for key, value in form.items():
            filter1 = key
            value1 = value
            query = { filter1: value1 }
    # Filter based on two fields returned
    elif len(form) == 2:
        if 'recipe_type' in form:
            filter1 = 'recipe_type'
            value1 = str(form['recipe_type'])
            if 'category' in form:
                filter2 = 'category'
                value2 = str(form['category'])
            elif 'genres' in form:
                filter2 = 'genres'
                value2 = str(form['genres'])
            else:
                filter2 = 'origin'
                value2 = str(form['origin'])
        elif 'category' in form:
            filter1 = 'category'
            value1 = str(form['category'])
            if 'genres' in form:
                filter2 = 'genres'
                value2 = str(form['genres'])
            else:
                filter2 = 'origin'
                value2 = str(form['origin'])
        else:
            filter1 = 'genres'
            value1 = str(form['genres'])
            filter2 = 'origin'
            value2 = str(form['origin'])
        query = ( { '$and' : [{ filter1 : value1 }, { filter2 : value2 }]})
        # Filter based on 3 fields returned
    elif len(form) == 3:
        if 'recipe_type' in form:
            filter1 = 'recipe_type'
            value1 = str(form['recipe_type'])
            if 'category' in form:
                filter2 = 'category'
                value2 = str(form['category'])
                if 'genres' in form:
                    filter3 = 'genres'
                    value3 = str(form['genres'])
                else:
                    filter3 = 'origin'
                    value3 = str(form['origin'])
            elif 'genres' in form:
                filter2 = 'genres'
                value2 = str(form['genres'])
                filter3 = 'origin'
                value3 = str(form['origin'])
        else:
            filter1 = 'category'
            value1 = str(form['category'])
            filter2 = 'genres'
            value2 = str(form['genres'])
            filter3 = 'origin'
            value3 = str(form['origin'])
        query = ( { '$and' : [{ filter1 : value1 }, { filter2 : value2 }, { filter3 : value3 }]})
        # Filter based on all fields returned
    else:
        filter1 = 'recipe_type'
        value1 = str(form['recipe_type'])
        filter2 = 'category'
        value2 = str(form['category'])
        filter3 = 'genres'
        value3 = str(form['genres'])
        filter4 = 'origin'
        value4 = str(form['origin'])
        query = ( { '$and' : [{ filter1 : value1 }, { filter2 : value2 }, { filter3 : value3 }, { filter4 : value4 }]} )
    return query

# get_media filter
def filter_media(form):
    # Filter based on one field returned
    if len(form) == 1:
        for key, value in form.items():
            filter1 = key
            value1 = value
            query = { filter1: value1 }
    # Filter based on two fields returned
    elif len(form) == 2:
        if 'category' in form:
            filter1 = 'category'
            value1 = str(form['category'])
            if 'genres' in form:
                filter2 = 'genres'
                value2 = str(form['genres'])
            else:
                filter2 = 'origin'
                value2 = str(form['origin'])
        else:
            filter1 = 'genres'
            value1 = str(form['genres'])
            filter2 = 'origin'
            value2 = str(form['origin'])
        query = ( { '$and': [{ filter1: value1 }, { filter2: value2 }]})
    # Filter based on three fields returned
    else:
        filter1 = 'category'
        value1 = str(form['category'])
        filter2 = 'genres'
        value2 = str(form['genres'])
        filter3 = 'origin'
        value3 = str(form['origin'])
        query = ( { '$and': [{ filter1: value1 }, { filter2: value2 }, { filter3: value3 }]})
    return query