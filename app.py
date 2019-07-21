import os
from flask import Flask, render_template, url_for, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Database access config
app.config['MONGO_DBNAME'] = 'binge_watch'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# Home Page display
@app.route('/')
@app.route('/index')
def home_page():
    return render_template('index.html')

""" Queries """

# Get all recipes
@app.route('/get_recipes')
def get_recipes():
    return render_template('recipe-results.html',
                            recipes = mongo.db.recipes.find())

# Find specific recipe
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    return render_template('recipe.html',
                            recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)}))

# Search recipes
@app.route('/search_recipes', methods=['GET', 'POST'])
def search_recipes():
    # Request the search term submitted as part of the form on index.html
    search_term = request.form.get('search_term')
    # Create index
    mongo.db.recipes.create_index([('$**', 'text')])
    # Build query
    query = ({ '$text': { '$search': search_term } })
    # Find results
    results = mongo.db.recipes.find(query)
    return render_template('recipe-results.html',
                            recipes = results)

# Run app
if __name__ == 'main':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')))