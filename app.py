from flask import Flask, request
# from flask_restful import reqparse, abort, Api, Resource
import os
import psycopg2
import api_utils 
import config

# import rest_api.api_utils
# import rest_api.config
# from rest_api.config import Config
from dotenv import load_dotenv

load_dotenv()

# instantiate Flask app
app = Flask(__name__)
# api = Api(app)

# get databse URL from config.py
url = config.Config.DATABASE_URL

# connect to database through URL
connection = psycopg2.connect(url)

# look up dishes by ingredients resource
@app.route("/dishes")
def get_dishes():

    ingredients = request.args.getlist("ingredients")

    print(f"Making get request to w/ {ingredients}")
    print(f"type(ingredients): {type(ingredients)}")

    res = api_utils.getDishes(
        conn = connection,
        table_name = "dish_db",
        ingredients = ingredients,
        limit = 5
        )
    return res

# run app
if __name__ == '__main__':
    app.run(debug=True)