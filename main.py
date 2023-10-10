import psycopg2
from psycopg2 import sql
import sqlalchemy
from typing import Union

from fastapi import Depends, FastAPI, HTTPException,  Query
from sqlalchemy.orm import Session
from config import Config

# from . import api_utils
import api_utils
import json

# from .database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Database connection function
def get_db_conn():
    conn = psycopg2.connect(
        dbname=Config.DATABASE_NAME,
        user=Config.DATABASE_USER,
        password=Config.DATABASE_PW,
        host=Config.DATABASE_HOST,
        port=Config.DATABASE_PORT
    )

    return conn

# look up dishes by ingredients resource
@app.get("/dishes/")
def get_dishes(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Making get request to w/ {ingredients}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # json encode the ingredients list
        ingredients = json.dumps(ingredients)
        # ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"
    
        # limit the highest number of results to return
        if limit and limit > 100:
            limit = 100

        # if a limit was specified, use it, otherwise return all results
        if limit:
            query = sql.SQL("""
                        SELECT dish, ingredients
                        FROM dish_table
                        WHERE ingredients -> 'ingredients' @> %s
                        LIMIT {}
                        """).format(sql.Literal(limit))
            
        else:
            query = sql.SQL("""
                        SELECT dish, ingredients
                        FROM dish_table
                        WHERE ingredients -> 'ingredients' @> %s
                        """)
        # Execute the query with the specified ingredient
        cursor.execute(query, (ingredients, ))

        # Commit changes to the database
        conn.commit()

        # Fetch all the rows that match the query
        db_rows = cursor.fetchall() 
    
        # convert the returned dishes to a key-value pair (dish: ingredients)
        dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

        return dishes
    
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

    # ingredients = request.args.getlist("ingredients")

    # print(f"Making get request to w/ {ingredients}")
    # print(f"type(ingredients): {type(ingredients)}")

    # res = api_utils.getDishes(
    #     conn = connection,
    #     table_name = "dish_table",
    #     ingredients = ingredients,
    #     limit = 5
    #     )
    # return res

# # Fast API 
# from typing import Union
# from fastapi import FastAPI

# # # Database packages
# import psycopg2
# from psycopg2 import sql
# import sqlalchemy
# from sqlalchemy import create_engine
# import json

# # # load environment variables, config, and API functions
# import os
# import api_utils 
# import config
# from dotenv import load_dotenv

# # load .env file
# load_dotenv()

# # # instantiate FastAPI app
# # app = FastAPI()

# # # get databse URL from config.py
# db_url = config.Config.DATABASE_URL
# db_host = config.Config.DATABASE_HOST
# db_name = config.Config.DATABASE_NAME
# db_user = config.Config.DATABASE_USER
# db_pw = config.Config.DATABASE_PW
# db_port = config.Config.DATABASE_PORT

# connection = psycopg2.connect(
#     database=db_name,
#     user=db_user,
#     password= db_pw,
#     host=db_host,
#     port=db_port
# )
# limit = 5
# table_name = "dish_table"
# ingredients = ['chicken', 'bacon']

# ingredients = json.dumps(ingredients)
# # ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"

# query = sql.SQL("""
#             SELECT *
#             FROM {}
#             WHERE ingredients -> 'ingredients' @> %s
#             LIMIT {}
#             """).format(sql.Identifier(table_name), sql.Literal(limit))
    

# # Create cursor object to interact with the database
# cur = connection.cursor()

# # Execute the query with the specified ingredient
# cur.execute(query, (ingredients, ))

# # Commit changes to the database
# connection.commit()

# # Fetch all the rows that match the query
# db_rows = cur.fetchall() 

# # convert the returned dishes to a key-value pair (dish: ingredients)
# dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

# cur.close()
# # look up dishes by ingredients resource
# @app.route("/dishes")
# def get_dishes():

#     ingredients = request.args.getlist("ingredients")

#     print(f"Making get request to w/ {ingredients}")
#     print(f"type(ingredients): {type(ingredients)}")

#     res = api_utils.getDishes(
#         conn = connection,
#         table_name = "dish_table",
#         ingredients = ingredients,
#         limit = 5
#         )
#     return res

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

# # Flask and flask_lambda pacakages
# from flask import Flask, request
# import json
# # from flask import request

# # # Database packages
# import psycopg2
# from psycopg2 import sql
# import sqlalchemy
# from sqlalchemy import create_engine

# # # load environment variables, config, and API functions
# import os
# import api_utils 
# import config
# from dotenv import load_dotenv


# load_dotenv()

# # instantiate Flask app
# app = Flask(__name__)
# # api = Api(app)

# # get databse URL from config.py
# db_url = config.Config.DATABASE_URL
# db_host = config.Config.DATABASE_HOST
# db_name = config.Config.DATABASE_NAME
# db_user = config.Config.DATABASE_USER
# db_pw = config.Config.DATABASE_PW
# db_port = config.Config.DATABASE_PORT

# connection = psycopg2.connect(
#     database=db_name,
#     user=db_user,
#     password= db_pw,
#     host=db_host,
#     port=db_port
# )

# # look up dishes by ingredients resource
# @app.route("/dishes")
# def get_dishes():

#     ingredients = request.args.getlist("ingredients")

#     print(f"Making get request to w/ {ingredients}")
#     print(f"type(ingredients): {type(ingredients)}")

#     res = api_utils.getDishes(
#         conn = connection,
#         table_name = "dish_table",
#         ingredients = ingredients,
#         limit = 5
#         )
#     return res


# # look up directions by ingredients resource
# @app.route("/direction")
# def get_directions():

#     dishes = request.args.getlist("dishes")

#     print(f"Making get request to w/ {dishes}")
#     print(f"type(dishes): {type(dishes)}")

#     res = api_utils.getDirections(
#         conn = connection,
#         table_name  = "dish_table",
#         dishes = dishes,
#         limit = 5
#         )
#     return res

# # run app
# if __name__ == '__main__':
#     app.run(debug=True)

##################################
# OLD VERSION USING FLASK-RESTFUL
##################################

# from flask import Flask, request
# from flask_restful import reqparse, abort, Api, Resource
# import os
# import psycopg2
# import api_utils 
# import config

# # import rest_api.api_utils
# # from rest_api.config import Config
# # from dotenv import load_dotenv

# # load_dotenv()

# # instantiate Flask app
# app = Flask(__name__)
# api = Api(app)

# # get databse URL from config.py
# url = config.Config.DATABASE_URL

# # connect to database through URL
# connection = psycopg2.connect(url)

# # placeholder for home resource
# class DishDatabase(Resource):

#     def get(self):
#         print(f"Making get request to w/ Chicken and bacon")
#         res = api_utils.getDishes2(
#             conn = connection,
#             table_name = "dish_db",
#             ingredients = ['chicken', 'bacon'],
#             limit = 5
#             )
        
#         return res
    
# # look up dishes by ingredients resource
# class FindDishes(Resource):
#     def get(self):

#         ingredients = request.args.getlist("ingredients")

#         print(f"Making get request to w/ {ingredients}")
#         print(f"type(ingredients): {type(ingredients)}")

#         res = api_utils.getDishes2(
#             conn = connection,
#             table_name = "dish_db",
#             ingredients = ingredients,
#             limit = 2
#             )
#         return res

# # add resources to api
# api.add_resource(DishDatabase, '/')
# api.add_resource(FindDishes, '/dishes')

# # run app
# if __name__ == '__main__':
#     app.run(debug=True)
