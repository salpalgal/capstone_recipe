from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import requests
from api_key import api_key
from forms import SignUpForm, LoginForm , RecipeSearchForm, EditProfileForm
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Recipe, Favorite

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

@app.route("/")
def root():
    return render_template("root.html", user = g.user)

@app.route("/home")
def home():
    if g.user:
        user = g.user
        
        return render_template("home.html", user = g.user)
    else:
        flash("please login","error")
        return redirect("/")

@app.route("/user/<int:user_id>/edit", methods = ["GET","POST"])
def profile_update(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = g.user 
    form = EditProfileForm(obj = user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data 
        user.image_url = form.image_url.data
        db.session.commit()
        return redirect(f"/user/{user.id}") 
    else:
        return render_template("edit_profile.html", form = form, user = user)

@app.route("/user/<int:user_id>")
def user_page(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    res = []
    favs = user.favorites
    for fav in favs:
        data = requests.get(f"https://api.spoonacular.com/recipes/{fav.api_recipe_id}/summary?apiKey={api_key}")
        res.append(data.json())
    
    return render_template("user_page.html", favs = favs, res = res ,user = user )

@app.route("/recipe/<int:recipe_id>/unfav", methods = ["POST"])
def unfav(recipe_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = g.user
    fav = Favorite.query.filter(Favorite.recipe_id == recipe_id).first()
    db.session.delete(fav)
    db.session.commit()
    return redirect(f"/user/{user.id}")

@app.route("/recipe/<int:recipe_id>/fav", methods = ["POST"])
def fav(recipe_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = g.user
    fav = Favorite(user_id = user.id, recipe_id = recipe_id)
    db.session.add(fav)
    db.session.commit()
    flash("added to favorite list", "success")
    return redirect(f"/list")
    

@app.route("/recipe/<int:recipe_id>/details")
def details(recipe_id):
    # recipe = Recipe.query.get_or_404(recipe_id)
    recipe = Recipe.query.get(recipe_id)
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    summary = requests.get(f"https://api.spoonacular.com/recipes/{recipe.api_recipe_id}/summary?apiKey={api_key}")
    sum_data  = summary.json()
    ingredients = requests.get(f"https://api.spoonacular.com/recipes/{recipe.api_recipe_id}/ingredientWidget.json?apiKey={api_key}")
    nutrition = requests.get(f"https://api.spoonacular.com/recipes/{recipe.api_recipe_id}/nutritionWidget.json?apiKey={api_key}")
    steps = requests.get(f"https://api.spoonacular.com/recipes/{recipe.api_recipe_id}/analyzedInstructions?apiKey={api_key}")
    return render_template("details.html", steps = steps.json(), user = g.user, nutrition = nutrition.json(), summary = sum_data, ingredients = ingredients.json())
    

@app.route("/search", methods = ["GET", "POST"])
def search():
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    form = RecipeSearchForm()
    if form.validate_on_submit():
        ingredients = form.ingredients.data
        number = form.number.data
        res =  requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}",params={"ingredients": ingredients ,"number": number})
        session["res"] = res.json()
    

        return redirect(url_for('.search_list',res = res) )
    else:
        return render_template("search.html", form= form, user= g.user)    

@app.route("/list")
def search_list():
    if not session["res"]:
        res = []
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    # res = requests.get(f"https://api.spoonacular.com/recipes/findByIngredients?apiKey={api_key}",params={"ingredients":"chicken","number": 1})
    # res = requests.post(f"https://api.spoonacular.com/recipes/analyzeInstructions", params = {"apiKey": api_key,"id": 632075})
    # res = requests.get(f"https://api.spoonacular.com/recipes/632075/analyzedInstructions?apiKey={api_key}")
    res = session["res"]
    # data = res.json()
    user = g.user 
    recipes = []

    for data in res:
        recipe = Recipe( user_id = user.id, api_recipe_id = data['id'])
        db.session.add(recipe)
        db.session.commit()
        r = Recipe.query.filter(Recipe.api_recipe_id == data["id"]).first()
        recipes.append(r)

    return render_template("search_list.html", data= res ,user = user,recipes = recipes)


@app.route("/signup", methods = ["GET","POST"])
def signup():
    user = g.user
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
    user = g.user
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            # flash(f"Hello, {user.username}!", "success")
            return redirect("/home")
        
    return render_template("login.html", form = form, user = user)

@app.route("/logout")
def logout():
    do_logout()
    return redirect("/")
