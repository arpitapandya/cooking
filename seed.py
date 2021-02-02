"""seed the database"""

from models import db, connect_db, User, UserRecipe, Recipe, Step, Ingredient, Measurement, ListIngredient, GroceryList
from app import app

# Create all tables
db.drop_all()
db.create_all()

# Add Users
kelly = User(username="kelly", email="test@test.in", password="pass123")
kim = User(username="kim", email="test@test.in", password="password123")
ken = User(username="ken", emai="test@test.in", password="password123")

# Add new Users
db.session.add(kelly)
db.session.add(kim)
db.session.add(ken)

db.session.commit()