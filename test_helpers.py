from unittest import TestCase

from models import User, db, Recipe, Ingredient, Measurement, Step
from helpers import CURRENT_USER_KEY, generate_headers, generate_search_params, create_login_data, add_user_data
from secrets import api_key

class TestData():
    def __init__(self, data):
        self.data = data


class TestForm():
    def __init__(self, username, password, email, img_url):
        self.username = username
        self.password = password
        self.email = email
        self.img_url = img_url

form = TestForm(username=TestData("test"), password=TestData(
    "testword"), email=TestData("test@test.com"), img_url=TestData("test_url"))

class HelperTestCase(TestCase):
    """ Unit tests for helper functions """

    def test_generate_headers(self):
        """ generate_headers tests """
        self.assertIsInstance(generate_headers(), object)
        self.assertEqual(generate_headers(), {
            'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
            'x-rapidapi-key': api_key
        })

    def test_generate_search_params(self):
        """ generate_headers tests """
        self.assertIsInstance(generate_search_params("test"), object)
        self.assertEqual(generate_search_params("test", "testly"), {
            "apiKey": api_key,
            "query": 'test',
            "cuisine": "testly",
            "diet": None,
            "offset": 0,
            "number": 12
        })

    def test_add_user_data(self):
        """ generate_user_data tests """
        self.assertIsInstance(create_login_data(form), object)
        self.assertEqual(add_user_data(form), {
            'username': form.username.data,
            'password': form.password.data,
            'email': form.email.data,
            'img_url': form.img_url.data
        })

    def test_create_login_data(self):
        """ create_user_data tests """
        self.assertIsInstance(create_login_data(form), object)
        self.assertEqual(create_login_data(form), {
            'username' : form.username.data,
            'password' : form.password.data,
        })