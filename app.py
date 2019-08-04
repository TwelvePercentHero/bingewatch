import os, datafunctions, math
from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
# Adding flask_uploads to allow custom recipe images to be uploaded by users
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Flask_uploads configuration for image uploads
images = UploadSet('images', IMAGES)
app.config['UPLOADED_IMAGES_DEST'] = '../static/images/uploads'
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
                    return redirect(url_for('profile',
                                            user=user_in_db['username']))
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
        user_likes = mongo.db.likes.find( { 'username': user_in_db['username']} )
        recipes = mongo.db.recipes.find()
        media = mongo.db.media.find()
        return render_template('profile.html',
                                user = user_in_db,
                                likes = user_likes,
                                recipes = recipes,
                                media = media)
    else:
        flash('You must be logged in!')
        return redirect(url_for('home_page'))

""" Recipe Queries """

# Get all recipes
@app.route('/get_recipes/<page_no>', methods=['GET', 'POST'])
def get_recipes(page_no):
    selected_recipe_type = None
    selected_category = None
    selected_genre = None
    selected_origin = None
    recipes = mongo.db.recipes
    page_skip = (int(page_no) - 1) * 9
    if request.method == 'POST':
        # Create dict from form fields to filter results
        form = request.form.to_dict()
        if 'recipe_type' in form:
            selected_recipe_type = form['recipe_type']
        if 'category' in form:
            selected_category = form['category']
        if 'genres' in form:
            selected_genre = form['genres']
        if 'origin' in form:
            selected_origin = form['origin']
        # Catch if users attempt to submit filters without selecting options
        if len(form) == 0:
            flash("Please choose a category to filter")
            return redirect(url_for('get_recipes', page_no = 1))
        query = datafunctions.filter_recipes(form)
        filtered_results = recipes.find(query).sort('recipe_name', 1)
        # Count total number of filtered recipes
        total_recipes = filtered_results.count()
        # If the total number of recipes is greater than 9, include pagination
        if total_recipes > 9:
            results_pages = recipes.find(query).sort('recipe_name', 1).skip(page_skip).limit(9)
        else:
            results_pages = filtered_results
    else:
        all_results = recipes.find().sort('recipe_name', 1)
        # Count total number of recipes
        total_recipes = all_results.count()
        # If the total number of recipes is greater than 9, include pagination
        if total_recipes > 9:
            results_pages = recipes.find().sort('recipe_name', 1).skip(page_skip).limit(9)
        else:
            results_pages = all_results
    # Calculate total number of pages needed
    total_pages = int(math.ceil(total_recipes/9.0))
    if total_recipes == 0:
        page_no = 0
    return render_template('recipe-results.html',
                            page_no = page_no,
                            total_results = total_recipes,
                            total_pages = total_pages,
                            recipes = results_pages,
                            recipe_types = mongo.db.recipe_types.find(),
                            genres = mongo.db.genres.find(),
                            origin = mongo.db.origin.find(),
                            categories = mongo.db.categories.find(),
                            selected_recipe_type = selected_recipe_type,
                            selected_category = selected_category,
                            selected_genre = selected_genre,
                            selected_origin = selected_origin)

# Find specific recipe
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    current_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('recipe.html',
                            recipe = current_recipe,
                            media = mongo.db.media.find().sort('media_name', 1))

# Search recipes
@app.route('/search_recipes/<page_no>', methods=['GET', 'POST'])
def search_recipes(page_no):
    selected_recipe_type = None
    selected_category = None
    selected_genre = None
    selected_origin = None
    recipes = mongo.db.recipes
    page_skip = (int(page_no) - 1) * 9
    # Request the search term submitted as part of the form on index.html
    search_term = request.form.get('search_term')
    # Create index
    recipes.create_index([('$**', 'text')])
    # Build query
    query = ({ '$text': { '$search': search_term } })
    # Find results
    recipe_results = recipes.find(query).sort('recipe_name', 1)
    # Count total number of returned recipes
    total_recipes = recipe_results.count()
    # If the total number of recipes is greater than 9, include pagination
    if total_recipes > 9:
        results_pages = recipes.find(query).sort('recipe_name', 1).skip(page_skip).limit(9)
    else:
        results_pages = recipe_results
    # Calculate total number of pages needed
    total_pages = int(math.ceil(total_recipes/9.0))
    if total_recipes == 0:
        page_no = 0
    return render_template('recipe-results.html',
                            page_no = page_no,
                            total_results = total_recipes,
                            total_pages = total_pages,
                            recipes = results_pages,
                            recipe_types = mongo.db.recipe_types.find(),
                            genres = mongo.db.genres.find(),
                            origin = mongo.db.origin.find(),
                            categories = mongo.db.categories.find(),
                            selected_recipe_type = selected_recipe_type,
                            selected_category = selected_category,
                            selected_genre = selected_genre,
                            selected_origin = selected_origin)

""" Media Queries """

# Get all media
@app.route('/get_media/<page_no>', methods=['GET', 'POST'])
def get_media(page_no):
    selected_category = None
    selected_genre = None
    selected_origin = None
    media = mongo.db.media
    page_skip = (int(page_no) - 1) * 9
    if request.method == 'POST':
        # Create dict from form fields to filter results
        form = request.form.to_dict()
        if 'category' in form:
            selected_category = form['category']
        if 'genres' in form:
            selected_genre = form['genres']
        if 'origin' in form:
            selected_origin = form['origin']
        # Catch if users attempt to submit filters without selecting options
        if len(form) == 0:
            flash("Please choose a category to filter")
            return redirect(url_for('get_media', page_no = 1))
        query = datafunctions.filter_media(form)
        filtered_media = mongo.db.media.find(query).sort('media_name', 1)
        # Count total number of filtered media
        total_media = filtered_media.count()
        # If the total number of media is greater than 9, include pagination
        if total_media > 9:
            media_pages = media.find(query).sort('media_name', 1).skip(page_skip).limit(9)
        else:
            media_pages = filtered_media
    else:
        all_media = mongo.db.media.find().sort('media_name', 1)
        # Count total number of media
        total_media = all_media.count()
        # If the total number of media is greater than 9, include pagination
        if total_media > 9:
            media_pages = media.find().sort('media_name', 1).skip(page_skip).limit(9)
        else:
            media_pages = all_media
    # Calculate total number of pages needed
    total_pages = int(math.ceil(total_media / 9.0))
    if total_media == 0:
        page_no = 0
    return render_template('media-results.html',
                            page_no = page_no,
                            total_results = total_media,
                            total_pages = total_pages,
                            media = media_pages,
                            categories = mongo.db.categories.find(),
                            origin = mongo.db.origin.find(),
                            genres = mongo.db.genres.find(),
                            selected_category = selected_category,
                            selected_genre = selected_genre,
                            selected_origin = selected_origin)

# Find specific media
@app.route('/media/<media_id>')
def media(media_id):
    media = mongo.db.media.find_one({'_id': ObjectId(media_id)})
    return render_template('media.html',
                            media = media,
                            recipes = mongo.db.recipes.find().sort('recipe_name', 1))

# Search media
@app.route('/search_media/<page_no>', methods=['GET', 'POST'])
def search_media(page_no):
    selected_category = None
    selected_genre = None
    selected_origin = None
    media = mongo.db.media
    page_skip = (int(page_no) - 1) * 9
    # Request the search term submitted as part of the form on index.html
    search_term = request.form.get('search_term')
    # Create index
    media.create_index([('$**', 'text')])
    # Build query
    query = ({ '$text': { '$search': search_term } })
    # Find results
    media_results = mongo.db.media.find(query)
    # Count total number of returned media
    total_media = media_results.count()
    # If the total number of media is greater than 9, include pagination
    if total_media > 9:
        results_pages = media.find(query).sort('media_name', 1).skip(page_skip).limit(9)
    else:
        results_pages = media_results
    # Calculate total number of pages needed
    total_pages = int(math.ceil(total_media / 9.0))
    if total_media == 0:
        page_no = 0
    return render_template('media-results.html',
                            page_no = page_no,
                            total_results = total_media,
                            total_pages = total_pages,
                            media = results_pages,
                            categories = mongo.db.categories.find(),
                            origin = mongo.db.origin.find(),
                            genres = mongo.db.genres.find(),
                            selected_category = selected_category,
                            selected_genre = selected_genre,
                            selected_origin = selected_origin)

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
    user = mongo.db.users.find_one({ 'username': session['user'] })
    # Upload image to uploads folder and generate filepath
    if 'image' in request.files:
        filename = images.save(request.files['image'])
        filepath = '../static/images/uploads/' + filename
    else:
        filepath = '../static/images/uploads/default.jpg'
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
        'image': filepath,
        'submitted_by': user['username'],
        'likes': 0
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
    return redirect(url_for('preview_recipe',
                            new_recipe_id = new_recipe.inserted_id))

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
    flash("Recipe submitted!")
    return redirect(url_for('recipe',
                            recipe_id = submitted_recipes.inserted_id))

# Discard recipe
@app.route('/discard_recipe/<discard_recipe_id>')
def discard_recipe(discard_recipe_id):
    mongo.db.temp_recipes.remove({'_id': ObjectId(discard_recipe_id)})
    flash("Recipe discarded")
    return redirect(url_for('get_recipes', page_no = 1))

# Edit recipe
@app.route('/edit_recipe/<edit_recipe_id>')
def edit_recipe(edit_recipe_id):
    # Check user is logged in
    if 'user' in session:
        # Find recipe to be edited in recipes collection
        recipe_changes = mongo.db.recipes.find_one({'_id': ObjectId(edit_recipe_id)})
        # Insert the recipe into temp_recipes
        mongo.db.temp_recipes.insert_one(recipe_changes)
        # Remove the recipe from the recipes collection
        mongo.db.recipes.remove({'_id': ObjectId(edit_recipe_id)})
        # Find the recipe to be edited in temp_recipes collection
        editing_recipe = mongo.db.temp_recipes.find_one({'_id': ObjectId(edit_recipe_id)})
        return render_template('edit-recipe.html',
                                recipe = editing_recipe,
                                recipe_types = mongo.db.recipe_types.find(),
                                media = mongo.db.media.find(),
                                origin = mongo.db.origin.find())
    else:
        flash('You must be logged in to do that!')
        return redirect(url_for('login'))

# Update recipe
@app.route('/update_recipe/<update_recipe_id>', methods=['GET', 'POST'])
def update_recipe(update_recipe_id):
    if 'image' in request.form:
        filename = images.save(request.files['image'])
        filepath = '../static/images/uploads/' + filename
    else:
        filepath = '../static/images/default.jpg'
    temp_recipes = mongo.db.temp_recipes
    form = request.form.to_dict()
    flatForm = request.form.to_dict(flat=False)
    temp_recipes.update({'_id': ObjectId(update_recipe_id)},
    {
    'recipe_name': form['recipe_name'],
    'recipe_from': form['recipe_from'],
    'cuisine': form['cuisine'],
    'recipe_type': flatForm['recipe_type'],
    'recipe_description': form['recipe_description'],
    'ingredients': flatForm['ingredients'],
    'method': flatForm['method'],
    'image': filepath
    })
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
    return redirect(url_for('preview_recipe',
                            new_recipe_id = update_recipe_id))

# Delete recipe
@app.route('/delete_recipe/<delete_recipe_id>', methods=['POST'])
def delete_recipe(delete_recipe_id):
    recipes = mongo.db.recipes
    # Rather than deleting outright, move the recipe into the archived_recipes collection
    archived_recipes = mongo.db.archived_recipes
    delete = recipes.find_one({ '_id': ObjectId(delete_recipe_id)})
    form = request.form.to_dict()
    # User must confirm the recipe name before deleting
    if form['confirm-delete'] == delete['recipe_name']:
        archived_recipes.insert_one(delete)
        recipes.remove({'_id': ObjectId(delete_recipe_id)})
        flash("Recipe successfully deleted!")
        return redirect(url_for('get_recipes'))
    else:
        flash("Recipe Name does not match - delete recipe failed")
        return redirect(url_for('recipe',
                                recipe_id = delete_recipe_id))

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
    user = mongo.db.users.find_one({ 'username': session['user'] })
    # Upload image to uploads folder and create filepath
    if 'image' in request.form:
        filename = images.save(request.files['image'])
        filepath = '../static/images/uploads/' + filename
    else:
        filepath = '../static/images/uploads/default.jpg'
    temp_media = mongo.db.temp_media
    form = request.form.to_dict()
    flatForm = request.form.to_dict(flat=False)
    new_media = temp_media.insert_one(
        {
            'media_name': form['media-name'],
            'category': form['category'],
            'origin': form['origin'],
            'starring': flatForm['starring'],
            'creators': flatForm['creators'],
            'genres': flatForm['genres'],
            'description': form['description'],
            'image': filepath,
            'submitted_by': user['username'],
            'likes': 0
        }
    )
    return redirect(url_for('preview_media', new_media_id = new_media.inserted_id))

# Preview media
@app.route('/preview_media/<new_media_id>')
def preview_media(new_media_id):
    media_preview = mongo.db.temp_media.find_one({ '_id': ObjectId(new_media_id)})
    return render_template('media-preview.html', temp_media = media_preview)

# Submit media
@app.route('/submit_media/<submit_media_id>')
def submit_media(submit_media_id):
    temp_media = mongo.db.temp_media
    # Find the media in the temp_media collection
    submit = temp_media.find_one({ '_id': ObjectId(submit_media_id)})
    # Insert the media into the media collection
    submitted_media = mongo.db.media.insert_one(submit)
    # Remove the media from the temp_media collection
    temp_media.remove({ '_id': ObjectId(submit_media_id)})
    flash("Media submitted!")
    return redirect(url_for('media', media_id = submitted_media.inserted_id))

# Discard media
@app.route('/discard_media/<discard_media_id>')
def discard_media(discard_media_id):
    mongo.db.temp_media.remove({ '_id': ObjectId(discard_media_id)})
    flash("Media discarded")
    return redirect(url_for('get_media', page_no = 1))

# Edit media
@app.route('/edit_media/<edit_media_id>')
def edit_media(edit_media_id):
    # Check user is logged in
    if 'user' in session:
        # Find media to be edited in media collection
        media_changes = mongo.db.media.find_one({ '_id': ObjectId(edit_media_id)})
        # Insert the media into temp_media
        mongo.db.temp_media.insert_one(media_changes)
        # Remove the media from the media collection
        mongo.db.media.remove({ '_id': ObjectId(edit_media_id)})
        # Find the media to be edited in temp_media collection
        editing_media = mongo.db.temp_media.find_one({ '_id': ObjectId(edit_media_id)})
        return render_template('edit-media.html',
                                media = editing_media,
                                categories = mongo.db.categories.find(),
                                origin = mongo.db.origin.find(),
                                genres = mongo.db.genres.find())

# Update media
@app.route('/update_media/<update_media_id>', methods=['GET', 'POST'])
def update_media(update_media_id):
    if 'image' in request.form:
        filepath = request.form['image']
    elif 'image' in request.files:
        filename = images.save(request.files['image'])
        filepath = '../static/images/uploads/' + filename
    else:
        filepath = '../static/images/default.jpg'
    temp_media = mongo.db.temp_media
    form = request.form.to_dict()
    flatForm = request.form.to_dict(flat=False)
    temp_media.update({ '_id': ObjectId(update_media_id)},
    {
        'media_name': form['media-name'],
        'category': form['category'],
        'origin': form['origin'],
        'starring': flatForm['starring'],
        'creators': flatForm['creators'],
        'genres': flatForm['genres'],
        'description': form['description'],
        'image': filepath
    })
    return redirect(url_for('preview_media', new_media_id = update_media_id))

# Delete media
@app.route('/delete_media/<delete_media_id>', methods=['POST'])
def delete_media(delete_media_id):
    media = mongo.db.media
    # Rather than deleting outright, move the media into the archived_media collection
    archived_media = mongo.db.archived_media
    delete = media.find_one({ '_id': ObjectId(delete_media_id) })
    form = request.form.to_dict()
    # User must confirm the media name before deleting
    if form['confirm-delete'] == delete['media_name']:
        archived_media.insert_one(delete)
        media.remove({ '_id': ObjectId(delete_media_id)})
        flash("Media successfully deleted!")
        return redirect(url_for('get_media'))
    else:
        flash("Media Name does not match - delete media failed")
        return redirect(url_for('media',
                                media_id = delete_media_id))

""" Likes """

# Like recipe
@app.route('/like_recipe/<like_recipe_id>')
def like_recipe(like_recipe_id):
    recipe = mongo.db.recipes.find_one({ '_id': ObjectId(like_recipe_id) })
    # Check user is logged in
    if 'user' in session:
        user = mongo.db.users.find_one({ 'username' : session['user'] })
        # Find out if the user has liked the recipe already
        likes = mongo.db.likes.count( { '$and': [ { 'recipe_id': recipe['_id'] }, { 'username': user['username'] } ] })
        if likes == 1:
            flash("You have already liked this recipe!")
            return redirect(url_for('recipe',
                                    recipe_id = like_recipe_id))
        else:
            mongo.db.likes.insert_one(
                {
                    'recipe_id': recipe['_id'],
                    'username': user['username'],
                    'record_type': 'recipe'
                }
            )
            # Use aggregate method to join the likes and recipes collections
            mongo.db.likes.aggregate([
                {
                    '$lookup':
                    {
                        'from': 'recipes',
                        'localField': 'recipe_id',
                        'foreignField': '_id',
                        'as': 'liked_recipes'
                    }
                },
                # Use $mergeObjects to combine likes and recipes documents into the likes collection
                {
                    '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$arrayElemAt': ['$liked_recipes', 0 ] }, '$$ROOT' ] } }
                },
                { 
                    '$project': { 'liked_recipes': 0 } 
                },
                # Output aggregated data to the likes collection
                { 
                    '$out': 'likes'
                }
            ])
            mongo.db.recipes.update({ '_id': ObjectId(like_recipe_id) },
            {
                '$inc': { 'likes': 1 }
            })
            flash("Recipe liked!")
            return redirect(url_for('recipe',
                                    recipe_id = like_recipe_id))

# Like media
@app.route('/like_media/<like_media_id>')
def like_media(like_media_id):
    media = mongo.db.media.find_one({ '_id': ObjectId(like_media_id) })
    # Check user is logged in
    if 'user' in session:
        user = mongo.db.users.find_one({ 'username': session['user'] })
        # Find out if the user has liked the media already
        likes = mongo.db.likes.count( { '$and': [ { 'media_id': media['_id'] }, { 'username': user['username'] } ] } )
        if likes == 1:
            flash("You have already liked this media!")
            return redirect(url_for('media',
                                    media_id = like_media_id))
        else:
            mongo.db.likes.insert_one(
                {
                    'media_id': media['_id'],
                    'username': user['username'],
                    'record_type': 'media'
                }
                )
            # Use aggregate method to join the likes and media collections
            mongo.db.likes.aggregate([
                {
                    '$lookup':
                    {
                        'from': 'media',
                        'localField': 'media_id',
                        'foreignField': '_id',
                        'as': 'liked_media'
                    }
                },
                # Use $mergeObjects to combine likes and media into the likes collection
                {
                    '$replaceRoot': { 'newRoot': { '$mergeObjects': [ { '$arrayElemAt': ['$liked_media', 0 ] }, '$$ROOT' ] } }
                },
                { 
                    '$project': { 'liked_media': 0 } 
                },
                # Output aggregated data to the likes collection
                { 
                    '$out': 'likes'
                }
            ])
            mongo.db.media.update({ '_id': ObjectId(like_media_id) },
            {
                '$inc': { 'likes': 1 }
            })
            flash("Media liked!")
            return redirect(url_for('media',
                                    media_id = like_media_id))

# Run app
if __name__ == 'main':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')))