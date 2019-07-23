import os
from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Database access configuration
app.config['MONGO_DBNAME'] = 'binge_watch'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# Home Page display
@app.route('/')
def home_page():
    return render_template('index.html')

""" User Authentication """

# Login

@app.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        user_in_db = mongo.db.users.find_one({ 'username' : session['user'] })
        if user_in_db:
            flash('You are logged in already!')
            return redirect(url_for('profile', user=user_in_db['username']))
    else:
        return render_template('login.html')

@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    user_in_db = mongo.db.users.find_one({ 'username': form['username'] })
    if user_in_db:
        if check_password_hash(user_in_db['password'], form['password']):
            session['user'] = form['username']
            flash('You were logged in!')
            return redirect(url_for('profile', user=user_in_db['username']))
        else:
            flash('Wrong password or user name!')
            return redirect(url_for('login'))
    else:
        flash('You must be registered!')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        flash('You are already signed in!')
        return redirect(url_for('home_page'))
    if request.method == 'POST':
        form = request.form.to_dict()
        if form['password'] == form['password2']:
            user = mongo.db.users.find_one({ 'username' : form['username']})
            if user:
                flash("{form['username']} already exists!")
                return redirect(url_for('register'))
            else:
                hash_pass = generate_password_hash(form['password'])
                mongo.db.users.insert_one(
                    {
                        'username': form['username'],
                        'password': hash_pass
                    }
                )
                user_in_db = mongo.db.users.find_one({'username': form['username']})
                if user_in_db:
                    session['user'] = user_in_db['username']
                    return redirect(url_for('profile', user=user_in_db['username']))
                else:
                    flash("There was a problem saving your profile")
                    return redirect(url_for('register'))
        else:
            flash("Passwords don't match!")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out!')
    return redirect(url_for('home_page'))

@app.route('/profile/<user>')
def profile(user):
    if 'user' in session:
        user_in_db = mongo.db.users.find_one({ 'username': user })
        return render_template('profile.html', user=user_in_db)
    else:
        flash('You must be logged in!')
        return redirect(url_for('home_page'))

""" Queries """

# Get all recipes
@app.route('/get_recipes', methods=['GET', 'POST'])
def get_recipes():
    if request.method == 'POST':
        # Create dict from form fields to filter results
        form = request.form.to_dict()
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
        recipe_results = mongo.db.recipes.find(query).sort('recipe_name', 1)
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

""" Recipe create and edit functions """

@app.route('/add_recipe')
def add_recipe():
    if 'user' in session:
        return render_template('add-recipe.html',
                            recipe_types = mongo.db.recipe_types.find().sort('recipe_type', 1),
                            origin = mongo.db.origin.find().sort('nationality', 1))
    else:
        flash("You must be logged in to do that!")
        return redirect(url_for('home_page'))

@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes = mongo.db.recipes
    form = request.form.to_dict()
    recipes.insert_one(
        {
        'recipe_name': form['recipe_name'],
        'cuisine': form['cuisine'],
        'recipe_type': form['recipe_type'],
        'recipe_description': form['recipe_description'],
        'ingredients': form['ingredients'],
        'method': form['method']
        }
    )
    return redirect(url_for('get_recipes'))

# Run app
if __name__ == 'main':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')))