from models import User, db, Recipe, Step, Ingredient, RecipeIngredient
from flask import request, session
import os
import requests
from secrets import API_KEY

CURRENT_USER_KEY = "user_id"
API_BASE_URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"

valid_diets = ['vegan', 'vegetarian']
valid_cuisines = ['indian', 'chinese', 'spanish', 'african', 'southern', 'mexican', 'korean', 'japanese', 'american', 'german']

def do_login(user):
    """User Login"""

    session[CURRENT_USER_KEY] = user.id

def do_logout():
    """User Logout."""

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]

def add_user_data(form):
    """Form access for user data"""

    username = form.username.data
    password = form.password.data
    email = form.email.data
    img_Url = form.img_Url.data
    return {
        'username': username,
        'password': password,
        'email': email,
        'img_Url': img_Url
    }

def create_login_data(form):
    """form access for for user login data"""

    username = form.username.data
    password = form.password.data

    return {
        "username": username,
        "password": password
    }

def generate_headers(form):
    """Returns headers"""
    return {
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        'x-rapidapi-key': API_KEY
    }

def do_search_params(query=None, cuisine=None, diet=None, offset=0, number=12):

    return {
        "apikey": API_KEY,
        "query": query,
        "cuisine": cuisine,
        "diet": diet,
        "offset": offset,
        "number": number
    }

def add_and_commit(obj):
    """
    Add and commit an obj to the db
    Returns obj
    """
    db.session.add(obj)
    db.session.commit()
    return obj


def do_search(request):
    """
    Get recipes from user request from Spoonacular API
    Returns a response
    """
    query = request.args.get('query', "")
    cuisine = request.args.get('cuisine', "")
    diet = request.args.get('diet', "")
    offset = int(request.args.get('offset', 0))

    headers = generate_headers()
    querystring = generate_search_params(query, cuisine, diet, offset)

    response = requests.request(
        "GET", f"{API_BASE_URL}/recipes/search", headers=headers, params=querystring)

    return response


def get_recipe(id):
    """
    Get recipe information from API
    Returns a recipe object
    """
    headers = generate_headers()
    response = requests.request(
        'GET', f"{API_BASE_URL}/recipes/{id}/information", headers=headers, data={'apiKey': API_KEY, 'id': id})

    return response


def add_ingredients_to_db(recipe_data):
    """ 
    Add ingredients and measurements to the db
    recipe_data (obj): recipe data from the Spoonacular API with extendedIngredients - a list of ingredient objects 
    Returns a list of SQLAlchemy ingredient objects
    """
    ingredient_list = []
    for ingredient in recipe_data['extendedIngredients']:
        try:
            db_ingredient = Ingredient.query.filter_by(
                id=ingredient['id']).first()
            if db_ingredient:
                ingredient_list.append(db_ingredient)
            else:
                id = ingredient.get('id', None)
                name = ingredient.get('name', None)
                original = ingredient.get('original', None)

                new_ingredient = Ingredient(
                    id=id, name=name, original=original)

                new_ingredient = add_and_commit(new_ingredient)
                print(f"\n Created new ingredient {new_ingredient} \n")

                ingredient_list.append(new_ingredient)
                print(f"\n Ingredient added to list: {ingredient_list} \n")

                recipe_data = add_measurement_for_ingredient(
                    ingredient, recipe_data)

        except Exception as e:
            print(str(e))
            # import pdb
            # pdb.set_trace()
            db.session.rollback()
            continue
    return ingredient_list

def add_recipe_to_db(recipe_data):
    """
    Add a recipe to the db
    recipe_data (obj): recipe data from the Spoonacular API
    Returns the recipe from the db
    """
    id = recipe_data.get('id', None)
    title = recipe_data.get('title', None)
    image = recipe_data.get('image', None)
    sourceName = recipe_data.get('sourceName', None)
    sourceUrl = recipe_data.get('sourceUrl', None)
    readyInMinutes = recipe_data.get('readyInMinutes', None)
    servings = recipe_data.get('servings', None)
    instructions = recipe_data.get('instructions', None)
    vegetarian = recipe_data.get('vegetarian', None)
    vegan = recipe_data.get('vegan', None)
    glutenFree = recipe_data.get('glutenFree', None)
    dairyFree = recipe_data.get('dairyFree', None)
    sustainable = recipe_data.get('sustainable', None)
    ketogenic = recipe_data.get('ketogenic', None)

    recipe = Recipe(id=id, title=title, image=image, sourceName=sourceName, sourceUrl=sourceUrl,
                    readyInMinutes=readyInMinutes, servings=servings, instructions=instructions, vegetarian=vegetarian, vegan=vegan, glutenFree=glutenFree, dairyFree=dairyFree, sustainable=sustainable, ketogenic=ketogenic, whole30=whole30)
    try:
        recipe = add_and_commit(recipe)
    except Exception:
        # import pdb
        # pdb.set_trace()
        db.session.rollback()
        print(str(Exception))
        return "Recipe couldn't be saved. Please try again."

    ingredients = add_ingredients_to_db(recipe_data)
    for ingredient in ingredients:
        recipe.ingredients.append(ingredient)
        db.session.commit()

    return recipe