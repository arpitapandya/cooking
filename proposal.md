# Capstone Project Proposal

### Arpita Pandya

###### Goal for user

My goal for the capstone project is that, I want to create a website that allow users to search various recipes. I am very passionate about making new recipes, I used to search online recipes to make different dishes.That made me to build a website that allow such users like me. My target is for the user who is someone who have passion and understanding to cook new dishes.

###### Data

I am planning to utilize the [Spoonacular Api](https://spoonacular.com/food-api) for data. I intend to make use of endpoints to : search recipes and get information about ingredients and instructions for the recipe.

###### Approach

The API itself presents the issue of a free API key only permitting a limited number of calls per day.
The database schema for this project will include a table for users with a name, email, password (hashed for security), and optional fields for diet (string) and a list for intolerances (as strings) that can be added via the user profile. There will also be a table for any saved recipes. This table will include the recipe ID (use API ID), the recipe title, description, image url, source url, ready_in, and servings. These two tables will be connected via a many-to-many relationship. A third table will be for ingredients, with an id (use API ID), name, amount and unit of measurement. The ingredients and recipes tables will be connected via a many-to-many relationship.

This is the most many-to-many relationships I’ve worked with, and I’ll have to check my db for recipes to see if it has been saved already by another user before saving any new recipe information as this will be an extensive process, and each recipe will contain ingredients and steps that also need to be checked.

###### User Flow

User will have to create and account and log in to search the recipe. The search will include option to refine the search checkboxes for diets and cuisines and a recipe search based on user like. Each list item from the results will be represented with a card consisting the recipe title, image, instructions and list of ingredients, which will also allow to to know the "ready in" time and amount of servings. Each card will have a faovorite button.
Clicking on a card will navigate the user to a page where the user can view the recipe information (description, ingredients, steps, etc).

###### Goals

This is my first capstone project where i define my work based on expectations. I believe this website will be helpful to the user. If i will have a more time i would like to add more functionalities where user can add list for the grocery and email with shopping list.