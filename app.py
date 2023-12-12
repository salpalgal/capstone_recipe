from flask import Flask, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
import requests
from api_key import api_key

# from models import db, connect_db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipe_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# connect_db(app)

# db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def root():
    # res = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}",params={"ingredients":"chicken","number": 1})
    # res = requests.post(f"https://api.spoonacular.com/recipes/analyzeInstructions", params = {"apiKey": api_key,"id": 632075})
    res = requests.get(f"https://api.spoonacular.com/recipes/632075/analyzedInstructions?apiKey={api_key}")
    data = res.json()

    return render_template("home.html", data= data)
