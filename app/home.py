# app/home.py
from flask import Blueprint, render_template

# Define the blueprint
home = Blueprint('home', __name__)

# Create the route for the home page
@home.route('/')
def index():
    return render_template('welcome.html')
