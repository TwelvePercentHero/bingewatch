import os
from flask import Flask, render_template, url_for
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

# Recipe read methods
@app.route('/get_recipes')
def get_recipes():
    return render_template('recipe-results.html',
                            recipes = mongo.db.recipes.find())

# Run app
if __name__ == 'main':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', '5000')))