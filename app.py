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
@app.route('/get_recipes', methods=['GET', 'POST'])
def get_recipes():
    if request.method == 'POST':
        form = request.form.to_dict()
        if len(form) == 1:
            if 'recipe_type' in form:
                recipe_results = mongo.db.recipes.find(
                    {
                        'recipe_type': form['recipe_type']
                    }).sort('recipe_name', 1)
            elif 'category' in form:
                recipe_results = mongo.db.recipes.find(
                    {
                        'category': form['category']
                    }).sort('recipe_name', 1)
            elif 'genre' in form:
                recipe_results = mongo.db.recipes.find(
                    {
                        'genres': form['genre']
                    }).sort('recipe_name', 1)
            elif 'origin' in form:
                recipe_results = mongo.db.recipes.find(
                    {
                        'origin': form['origin']
                    }).sort('recipe_name', 1)
    else:
        recipe_results = mongo.db.recipes.find().sort('recipe_name', 1)
    return render_template('recipe-results.html',
                            recipes = recipe_results,
                            recipe_types = mongo.db.recipe_types.find(),
                            genres = mongo.db.genres.find(),
                            origin = mongo.db.origin.find(),
                            categories = mongo.db.categories.find())

# Find specific recipe
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    current_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('recipe.html',
                            recipe = current_recipe)

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