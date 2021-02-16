from flask import Flask, request, render_template, redirect, url_for, g, jsonify, flash, abort, session
from models import db, connect_db, User, Recipe, Ingredient, Step, UserRecipe, Measurement
from sqlalchemy.exc import IntegrityError

from forms import SignUpForm, LoginForm
from flask_debugtoolbar import DebugToolbarExtension
from helpers import add_user_data, create_login_data, generate_headers, generate_search_params, add_and_commit, do_search, get_recipe, do_login, do_logout, add_ingredients_to_db, add_recipe_to_db, add_measurement_for_ingredient, API_BASE_URL, valid_cuisines, valid_diets
from secrets import api_key
import requests
import os

app = Flask(__name__)
if __name__ == '__main__':
  app.run()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///meal_planner')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


toolbar = DebugToolbarExtension(app)
connect_db(app)
db.create_all()

CURRENT_USER_KEY = "user_id"
API_BASE_URL = "https://api.spoonacular.com"
# API_BASE_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"

API_KEY = api_key

@app.before_request
def add_user_to_g():
  """Add current user"""

  if CURRENT_USER_KEY in session:
    g.user = User.query.get(session[CURRENT_USER_KEY])
  
  else:
    g.user = None

    g.valid_diets = [diet for diet in valid_diets]
    g.valid_cuisines = [cuisines for cuisines in valid_cuisines]

@app.context_processor
def context_processor():
  """Global context jinja templates"""
  return dict(diets=valid_diets, cuisines=valid_cuisines)

###User Signup###
@app.route('/signup', methods=["GET", "POST"])
def signup():
  """ User Signup """

  form = SignUpForm()

  if form.validate_on_submit():
    user_data = add_user_data(form)

    try:
      user = User.signup(user_data)
      add_and_commit(user)
      db.session.commit()

    except IntegrityError as error:
      db.session.rollback()
      if (f'(username)=({user.username}) already exists') in error._message():
          flash("username already taken", 'danger')
      elif (f'(email)=({user.email}) already exists') in error._message():
          flash("Email already taken", 'danger')

      return render_template('users/signup.html', form=form)

    do_login(user)

    return redirect("/")

  else:
    return render_template('users/signup.html', form=form)

### User Login###

@app.route('/login', methods=["GET", "POST"])
def login():
  """ Handle user login."""

  form = LoginForm()

  if form.validate_on_submit():
    # user = User.authenticate(data)
    data = create_login_data(form)
    user = User.authenticate(data)
    
    if user:
      do_login(user)
      flash(f"Hello, {user.username}!", "success")
      return redirect("/")

    flash("Invalid Credentials.", 'danger')

  return render_template('users/login.html', form=form)


@ app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('You have been logged out', 'success')
    return redirect(url_for('home_page'))


####Search Routes####


@app.route('/')
def home_page():
  """ Home Page """
  return render_template('home.html')


@app.route('/load')
def load():
  """Load more results after the end of the page"""
  if request.args:
    response = do_search(request)
    data = response.json()

    if len(data['results']) == 0:
      return (jsonify(data=data), 200)
    
    user_favorites = [f.id for f in g.user.recipes]
    favorites = [r['id']for r in data['results'] if r['id'] in user_favorites]
    response_json = jsonify(data=data, favorites=favorites)
  return (response_json, 200)

@app.route('/search')
def search_recipes():
  """ Recipe Serach. """
  if not g.user:
    return abort(401)

  response = do_search(request)
  data = response.json()
  
  if len(data['results']) == 0:
    return (jsonify(data=data), 200)
  
  user_favorites = [f.id for f in g.user.recipes]
  favorites = [r['id'] for r in data['results'] if r['id'] in user_favorites]
  response_json = jsonify(data=data, favorites=favorites)

  return (response_json, 200)

#### User Routes####

@app.route('/users/<int:id>')
def view_user(id):
  """ Display user """
  if not g.user:
    flash('You must log in first', 'warning')
    return redirect(url_for('login'))

  return render_template('users/profile.html')

@ app.route('/users/<int:id>', methods=['PATCH'])
def update_user(id):
    """ Update user info """
    if not g.user:
        return abort(401)
    if request.json['id'] != id:
        return jsonify(errors="You don't have permission to do that!")

    try:
        user = User.query.get_or_404(id)
        new_email = request.json.get('email', user.email)
        new_img_url = request.json.get('imgUrl', user.img_url)
        if new_email:
            user.email = new_email
        if new_img_url:
            user.img_url = new_img_url

        db.session.commit()

        response_json = jsonify(user=user.serialize(),
                                message="Update successful!")
        return (response_json, 200)
    except Exception as e:
        return jsonify(errors=str(e))

@ app.route('/favorites/')
def view_saved_recipes():
    """ Route to view saved recipes """
    if not g.user:
        flash('You must be logged in to do that', 'warning')
        return redirect(url_for('login'))

    id_list = [recipe.id for recipe in g.user.recipes]

    return render_template('users/favorites.html', id_list=id_list)


@app.route('/favorites/<int:id>', methods=['POST'])
def add_favorite(id):
  """Add recipe to favorites"""
  if not g.user:
    return abort(401)

  recipe = Recipe.query.filter_by(id=id).first()

  if not recipe:
    response = get_recipe(id)
    data = response.json()

    recipe = add_recipe_to_db(data)
    g.user.recipes.append(recipe)
    db.session.commit()
  else:
    g.user.recipes.append(recipe)
    db.session.commit()
  
  response_json = jsonify(
    recipe=recipe.serialize(), message="Congrats Recipe added successfully!")
  return (response_json, 200)

@app.route('/favorites/<int:id>', methods=['DELETE'])
def remove_favorite(id):
  """Remove recipe from favorites"""
  if not g.user:
    return abort(401)
  try:
    recipe = Recipe.query.filter_by(id=id).first()
    UserRecipe.query.filter(
        UserRecipe.user_id == g.user.id, UserRecipe.recipe_id == recipe.id).delete()
    db.session.commit()
    response_json = jsonify(recipe=recipe.serialize(), message="Recipe removed!")
    return (response_json, 200)
  except Exception as e:
    print(str(e))
    return jsonify(errors=str(e))

@ app.route('/recipes/<int:id>')
def view_recipe_details(id):
    """ View recipe in detail """
    if not g.user:
        flash('You must be logged in to do that', 'warning')
        return redirect(url_for('login'))

    recipe = Recipe.query.filter_by(id=id).first()
    if not recipe:
        response = get_recipe(id)
        data = response.json()
        recipe = add_recipe_to_db(data)
        return render_template('recipes/details.html', recipe=recipe)
    else:
        return render_template('recipes/details.html', recipe=recipe)

@app.errorhandler(404)
def page_not_found(error):
  """404 NOT FOUND PAGE."""

  return render_template('errors/404.html'), 404