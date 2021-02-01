"""SQLAlchemy Models for Food Planner """

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """ Connect to database """
    db.app = app
    db.init_app(app)

class User(db.Model):
    """ User."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text)
    img_Url = db.Column(db.String, default='/static/images/cooking.png')
    is_admin = db.Column(db.Boolean, default=False)
    recipes = db.relationship('Recipe', secondary="users_recipes", backref='users')
    grocery_list = db.relationship('GroceryList', backref='user')

    @classmethod
    def signup(cls, data):
        """ Generate hashed password and register a new user """
        hashed = bcrypt.generate_password_hash(data['password'])
        # Turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=data['username'], password=hashed_utf8, email=data['email'], img_Url=data['img_Url'])

    # @classmethod
    # def signup(cls, data):
    #     """Sign up user hashes password and adds user to system."""

    # hashed = bcrypt.generate_password_hash(data['password'])
    # hashed_utf8 = hashed.decode("utf8")

    # return cls(username=data['username'], password=hashed_utf8, email=data['email'], image_url=data['image_url'])

    @classmethod
    def authenticate(cls, data):

        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            return user
        else:
            return False
    
    @classmethod
    def default_image(cls):
        return './static/images/icons8-kawaii-cupcake-64.png'

    def serialize(self):
        """ Serialize User instance for JSON """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'img_url': self.img_url,
            'is_admin': self.is_admin
        }
    def _repr_(self):
        return f'<User: {self.username}>'
   
class UserRecipe(db.Model):
    """ Many to many Users to Recipes """
    __tablename__ = "users_recipes"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete='CASCADE'), primary_key=True)

class Recipe(db.Model):
    """ Recipe. """

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    img_Url = db.Column(db.String, default="/static/images/recipe.png")
    source_Url = db.Column(db.String)
    description = db.Column(db.String)
    servings = db.Column(db.Integer)
    ready_in = db.Column(db.Integer)
    ingredients = db.relationship("Ingredient", secondary="recipes_ingredients", backref="recipes")
    steps = db.relationship("Step", backref="recipe")

    def _repr_(self):
        return f'<Recipe: {self.title}>'
    
    def serialize(self):
        """Serialize recipe instance for JSON """
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image,
            'source_url': self.sourceName,
            'ready_in': self.readyInMinutes,
            'servings': self.servings,
            'steps': self.steps,
            'instructions': self.instructions,
            'ingredients': self.ingredients
        }

class Step(db.Model):
    """ Many to many recipes to steps. """

    __tablename__ = "steps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    number = db.Column(db.Integer, nullable=False)
    step = db.Column(db.String)

    def _repr_(self):
        return f'<Step: {self.number}- {self.step}>'
    
    def show_step(self):
        """return string of steps"""
        return f"{self.number}. {self.step}"

    def serialize(self):
        """Ingredients serialize"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'number': self.number,
            'step': self.step
        }

class Ingredient(db.Model):
    """ Ingredient. """

    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    original = db.Column(db.String)

    def _repr_(self):
        return f'<Ingredient: {self.name}>'
    
    def serialize(self):
        """Serialize Ingredient instance for JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'original': self.original
        }


class RecipeIngredient(db.Model):
    """ Many to many Recipes to Ingredients. """

    __tablename__ = "recipes_ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"))
    amt = db.Column(db.Float)
    ingredient = db.relationship("Ingredient", backref="recipes_ingredients")
    recipe = db.relationship("Recipe", backref="recipes_ingredients")

    def show_recipeingredient(self):
        """ Returns a string with recipe ingredients"""
        return f"{{self.amt}} {self.ingredient.name}"

class ListIngredient(db.Model):
    """ List Ingredients for the recipe. """

    __tablename__ = "list_ingredients"

    list_id = db.Column(db.Integer, db.ForeignKey("grocerylist.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)

class GroceryList(db.Model):
    """ Grocery List for the ingredients required. """

    __tablename__ = "grocerylist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ingredients = db.relationship('Ingredient', secondary="list_ingredients", backref="grocerylist")