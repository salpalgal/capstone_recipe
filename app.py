from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
from api_key import api_key
from forms import SignUpForm, LoginForm
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipe_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    # user = g.user
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
        

@app.route("/home")
def root():
    # res = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}",params={"ingredients":"chicken","number": 1})
    # res = requests.post(f"https://api.spoonacular.com/recipes/analyzeInstructions", params = {"apiKey": api_key,"id": 632075})
    res = requests.get(f"https://api.spoonacular.com/recipes/632075/analyzedInstructions?apiKey={api_key}")
    data = res.json()

    return render_template("home.html", data= data)

@app.route("/signup", methods = ["GET","POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/home")
    else:
        return render_template("signup.html", form = form)

@app.route("/login", methods =["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            # flash(f"Hello, {user.username}!", "success")
            return redirect('/home')
        
    return render_template("login.html", form = form)
