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

    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String, default='/static/images/cooking.png')
    is_admin = db.Column(db.Boolean, default=False)
    recipes = db.relationship('Recipe', secondary="users_recipes", backref='users')
    # grocery_list = db.relationship('GroceryList', backref='user')

    @classmethod
    def signup(cls, data):
        """ Generate hashed password and register a new user """
        hashed = bcrypt.generate_password_hash(data['password'])
        # Turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=data['username'], password=hashed_utf8, email=data['email'], img_url=data['img_url'])

    # @classmethod
    # def signup(cls, data):
    #     """Sign up user hashes password and adds user to system."""

    # hashed = bcrypt.generate_password_hash(data['password'])
    # hashed_utf8 = hashed.decode("utf8")

    # return cls(username=data['username'], password=hashed_utf8, email=data['email'], image_url=data['image_url'])

    @classmethod
    def authenticate(cls, data):
        """ Validate the username and password """

        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            return user
        else:
            return False
    
    @classmethod
    def default_image(cls):
        return './static/images/lemon-2409365_1280.jpg'

    def serialize(self):
        """ Serialize User instance for JSON """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'img_url': self.img_url,
            'is_admin': self.is_admin
        }

    def __repr__(self):
        return f'<User: {self.username}>'
   
class UserRecipe(db.Model):
    """ Many to many Users to Recipes """

    __tablename__ = "users_recipes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete='CASCADE'), primary_key=True)

class Recipe(db.Model):
    """ Recipe. """

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    sourceName = db.Column(db.String, nullable=False)
    sourceUrl = db.Column(db.String)
    readyInMinutes = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    instructions = db.Column(db.String)
    vegetarian = db.Column(db.Boolean, default=False)
    vegan = db.Column(db.Boolean, default=False)
    glutenFree = db.Column(db.Boolean, default=False)
    dairyFree = db.Column(db.Boolean, default=False)
    sustainable = db.Column(db.Boolean, default=False)
    ketogenic = db.Column(db.Boolean, default=False)
    ingredients = db.relationship("Ingredient", secondary="measurements", backref="recipes")
    steps = db.relationship("Step", backref="recipe")

    def __repr__(self):
        return f'<Recipe: {self.title}>'
    
    def serialize(self):
        """Serialize recipe instance for JSON """
        return {
            'id': self.id,
            'title': self.title,
            'img_Url': self.image,
            'source_name': self.sourceName,
            'source_url': self.sourceUrl,
            'ready_in': self.readyInMinutes,
            'servings': self.servings,
            'instructions': self.instructions,
            'ingredients': [ingredient.serialize() for ingredient in self.ingredients],
            'steps': [step.serialize() for step in self.steps]
        }

class Step(db.Model):
    """ Many to many recipes to steps. """

    __tablename__ = "steps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    number = db.Column(db.Integer)
    step = db.Column(db.String)

    def __repr__(self):
        return f'<Step: {self.number} - {self.step}>'
    
    def show_step(self):
        """return string of steps"""
        return f"{self.number}.{self.step}"

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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    original = db.Column(db.String)

    def __repr__(self):
        return f'<Ingredient: {self.name}>'
    
    def serialize(self):
        """Serialize Ingredient instance for JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'original': self.original
        }


class Measurement(db.Model):
    """ Many to many Recipes to Ingredients. """

    __tablename__ = "measurements"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    amount = db.Column(db.Float)
    unit = db.Column(db.String)
    recipe = db.relationship("Recipe", backref="measurements")
    ingredient = db.relationship("Ingredient", backref="measurements")

    def show_measurement(self):
        """ Returns a string with recipe ingredients"""
        return f"{int(self.amount)} {self.unit} {self.ingredient.name}"

class ListIngredient(db.Model):
    """ List Ingredients for the recipe. """

    __tablename__ = "lists_ingredients"

    list_id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)

# class GroceryList(db.Model):
#     """ Grocery List for the ingredients required. """

#     __tablename__ = "grocerylist"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String(50), nullable=False)
#     date_created = db.Column(db.DateTime, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     ingredients = db.relationship('Ingredient', secondary="list_ingredients", backref="grocerylist")