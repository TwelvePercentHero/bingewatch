import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def home_page():
    return render_template('index.html')