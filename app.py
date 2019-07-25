import os
from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
# Adding flask_uploads to allow custom recipe images to be uploaded by users
from flask_uploads import UploadSet, configure_uploads, IMAGES


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Flask_uploads configuration for image uploads
images = UploadSet('images', IMAGES)
app.config['UPLOADED_IMAGES_DEST'] = 'static/images/uploads'
configure_uploads(app, images)

# Database access configuration
app.config['MONGO_DBNAME'] = 'binge_watch'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

# Home Page display
@app.route('/')
def home_page():
    return render_template('index.html')

""" User Authentication """

# Login Page
@app.route('/login', methods=['GET'])
def login():
    # Check if user is already logged in and redirect to profile page
    if 'user' in session:
        user_in_db = mongo.db.users.find_one({ 'username' : session['user'] })
        if user_in_db:
            flash('You are logged in already!')
            return redirect(url_for('profile', user=user_in_db['username']))
    else:
        return render_template('login.html')

# User authorisation
@app.route('/user_auth', methods=['POST'])
def user_auth():
    # Create dict from form fields
    form = request.form.to_dict()
    user_in_db = mongo.db.users.find_one({ 'username': form['username'] })
    if user_in_db:
        # Check entered password matches password in database after hashing
        if check_password_hash(user_in_db['password'], form['password']):
            session['user'] = form['username']
            flash('You were logged in!')
            return redirect(url_for('profile', user=user_in_db['username']))
        else:
            flash('Wrong password or user name!')
            return redirect(url_for('login'))
    else:
        flash('You must be registered!')
        return redirect(url_for('register'))

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is already logged in
    if 'user' in session:
        flash('You are already signed in!')
        return redirect(url_for('home_page'))
    # If method is POST check password1 and 2 match and check if user already exists in database
    if request.method == 'POST':
        form = request.form.to_dict()
        if form['password'] == form['password2']:
            user = mongo.db.users.find_one({ 'username' : form['username']})
            if user:
                flash(f"{form['username']} already exists!")
                return redirect(url_for('register'))
            # If user doesn't exist, generate password hash and insert into database
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

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out!')
    return redirect(url_for('home_page'))

# View user profile
@app.route('/profile/<user>')
def profile(user):
    # Check if user is logged in
    if 'user' in session:
        user_in_db = mongo.db.users.find_one({ 'username': user })
        return render_template('profile.html', user=user_in_db)
    else:
        flash('You must be logged in!')
        return redirect(url_for('home_page'))

""" Recipe Queries """

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

""" Media Queries """

# Get all media
@app.route('/get_media', methods=['GET', 'POST'])
def get_media():
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
        media = mongo.db.media.find(query).sort('media_name', 1)
    else:
        media = mongo.db.media.find().sort('media_name', 1)
    return render_template('media-results.html',
                            media = media,
                            categories = mongo.db.categories.find(),
                            origin = mongo.db.origin.find(),
                            genres = mongo.db.genres.find())

# Find specific media
@app.route('/media/<media_id>')
def media(media_id):
    media = mongo.db.media.find_one({'_id': ObjectId(media_id)})
    return render_template('media.html',
                            media = media)

# Search media
@app.route('/search_media', methods=['GET', 'POST'])
def search_media():
    search_term = request.form.get('search_term')
    mongo.db.media.create_index([('$**', 'text')])
    query = ({ '$text': { '$search': search_term } })
    results = mongo.db.media.find(query)
    return render_template('media-results.html',
                            media = results)

""" Recipe create and edit functions """

# Add recipe form
@app.route('/add_recipe')
def add_recipe():
    # Check user is logged in
    if 'user' in session:
        return render_template('add-recipe.html',
                            recipe_types = mongo.db.recipe_types.find().sort('recipe_type', 1),
                            origin = mongo.db.origin.find().sort('nationality', 1),
                            media = mongo.db.media.find().sort('media_name', 1))
    else:
        flash("You must be logged in to do that!")
        return redirect(url_for('login'))

# Insert recipe to database
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    # Upload image to uploads folder and generate filepath
    if 'image' in request.files:
        filename = images.save(request.files['image'])
        filepath = 'static/images/uploads/' + filename
    else:
        filepath = 'static/images/default.jpg'
    # Submits to temp_recipes collection to allow for preview without displaying in recipe-results
    temp_recipes = mongo.db.temp_recipes
    form = request.form.to_dict()
    # Create flatForm to allow recipe_type, ingredients and method to be stored as arrays rather than strings
    flatForm = request.form.to_dict(flat=False)
    # Insert into recipes collection
    new_recipe = temp_recipes.insert_one(
        {
        'recipe_name': form['recipe_name'],
        'recipe_from': form['recipe_from'],
        'cuisine': form['cuisine'],
        'recipe_type': flatForm['recipe_type'],
        'recipe_description': form['recipe_description'],
        'ingredients': flatForm['ingredients'],
        'method': flatForm['method'],
        'image': filepath
        }
    )
    # Use aggregate method to join the temp_recipes and media collections
    temp_recipes.aggregate([
        {
            '$lookup':
            {
                'from': 'media',
                'localField': 'recipe_from',
                'foreignField': 'media_name',
                'as': 'recipe_media'
            }
        },
        # Use $mergeObjects to combine temp_recipes and media documents into the temp_recipes collection
        {
            '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$arrayElemAt': [ '$recipe_media', 0 ]}, '$$ROOT'] } }
        },
        {
            '$project': { 'recipe_media': 0 }
        },
        # Output aggregated data to the temp_recipes collection
        {
            '$out': 'temp_recipes'
        }
    ])
    return redirect(url_for('preview_recipe', new_recipe_id = new_recipe.inserted_id))

# Preview recipe
@app.route('/preview_recipe/<new_recipe_id>')
def preview_recipe(new_recipe_id):
    recipe_preview = mongo.db.temp_recipes.find_one({'_id': ObjectId(new_recipe_id)})
    return render_template('recipe-preview.html',
                            temp_recipe = recipe_preview)

# Submit recipe
@app.route('/submit_recipe/<submit_recipe_id>')
def submit_recipe(submit_recipe_id):
    temp_recipes = mongo.db.temp_recipes
    # Find the recipe in temp_recipes collection
    submit = temp_recipes.find_one({'_id': ObjectId(submit_recipe_id)})
    # Insert the recipe into recipes collection
    submitted_recipes = mongo.db.recipes.insert_one(submit)
    # Remove the recipe from temp_recipes collection
    temp_recipes.remove({'_id': ObjectId(submit_recipe_id)})
    return redirect(url_for('recipe', recipe_id=submitted_recipes.inserted_id))

# Discard recipe
@app.route('/discard_recipe/<discard_recipe_id>')
def discard_recipe(discard_recipe_id):
    mongo.db.temp_recipes.remove({ '_id': ObjectId(discard_recipe_id)})
    flash("Recipe discarded")
    return redirect(url_for('get_recipes'))

""" Media create and edit functions """

# Add media form
@app.route('/add_media')
def add_media():
    # Check user is logged in
    if 'user' in session:
        return render_template('add-media.html',
                                categories = mongo.db.categories.find(),
                                origin = mongo.db.origin.find(),
                                genres = mongo.db.genres.find())
    else:
        flash("You must be logged in to do that!")
        return redirect(url_for('login'))

# Insert media to database
@app.route('/insert_media', methods=['POST'])
def insert_media():
    # Upload image to uploads folder and create filepath
    if 'image' in request.files:
        filename = images.save(request.files['image'])
        filepath = 'static/images/uploads/' + filename
    else:
        filepath = 'static/images/default.jpg'
    media = mongo.db.media
    form = request.form.to_dict()
    flatForm = request.form.to_dict(flat=False)
    media.insert_one(
        {
            'media_name': form['media-name'],
            'category': form['category'],
            'origin': form['origin'],
            'starring': flatForm['starring'],
            'creators': flatForm['creators'],
            'genres': flatForm['genres'],
            'description': form['description'],
            'image': filepath
        }
    )
    return redirect(url_for('get_media'))

# Run app
if __name__ == 'main':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')))