""" Forms for food planner app. """

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from flask_wtf.html5 import URLField, EmailField
from wtforms.validators import InputRequired, Email, Optional, EqualTo

class SignUpForm(FlaskForm):
    """Form for adding user."""

    username = StringField("Username", validators=[InputRequired(message="Please add Username")])
    email = EmailField("Email", validators=[InputRequired(message="Email required"), Email(message="Invalid !")])
    password = PasswordField("Password", validators=[InputRequired(message="Please create a Password")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(message="Please input the same Password")])
    img_Url = URLField("URL(Optional)", validators=[Optional()])

class LoginForm(FlaskForm):
    """ Login form."""

    username = StringField("Username", validators=[InputRequired(message="Username Required")])
    password = PasswordField("Password", validators=[InputRequired(message="Password Required")])

class GroceryListForm(FlaskForm):
    """ Grocery list form. """

    title = StringField("List Title", validators=[InputRequired(message="Add Title")])