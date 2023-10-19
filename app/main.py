from fastapi import Depends, FastAPI, HTTPException,  Query
from mangum import Mangum
import uvicorn

import psycopg2
from psycopg2 import sql
from typing import Union

from app.config import Config
import crud
import json

# instantiate FastAPI app
app = FastAPI()

# wrao the app in Mangum for AWS Lambda
handler = Mangum(app)

# function that makes a database connection
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
@app.get("/dishes-by-ingredients/")
def get_dishes_by_ingredients(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Making get request w/ {ingredients}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        dishes = crud._query_dishes_by_ingredients(conn=conn, cursor=cursor, ingredients=ingredients, limit=limit)
        return dishes
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

# TODO: internal error, function not working properly
# look up directions by dish_name
@app.get("/ingredients-by-dishes/")
def get_ingredients_by_dishes(dishes: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Making get request w/ {dishes}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        dishes = crud._query_ingredients_by_dishes(conn=conn, cursor=cursor, dishes=dishes, limit=limit)
        return dishes
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

# look up dishes by dish_id
@app.get("/dishes-by-id/")
def get_dishes_by_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting dishes by dish_id {dish_id}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        directions = crud._query_dishes_by_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
        return directions
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

# look up directions by ingredients resource
@app.get("/directions-by-id/")
def get_directions_by_dish_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting directions by dish_id {dish_id}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        directions = crud._query_directions_by_dish_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
        return directions
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

# look up dishes and match percentage by ingredients resource
@app.get("/percent_match-by-ingredients/")
def get_percent_match_by_ingredients(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Making get request to w/ {ingredients}")
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        percent_match = crud._query_percent_match_by_ingredients(conn=conn, cursor=cursor, ingredients=ingredients, limit=limit)
        return percent_match
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)

##########################
# OLD code to delete later
##########################

# TODO: DELETE old code below
# # look up dishes by ingredients resource
# @app.get("/dishes/")
# def get_dishes(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
#     print(f"Making get request to w/ {ingredients}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         # json encode the ingredients list
#         ingredients = json.dumps(ingredients)
#         # ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"
    
#         # limit the highest number of results to return
#         if limit and limit > 100:
#             limit = 100

#         # if a limit was specified, use it, otherwise return all results
#         if limit:
#             query = sql.SQL("""
#                         SELECT dish, ingredients
#                         FROM dish_table
#                         WHERE ingredients -> 'ingredients' @> %s
#                         LIMIT {}
#                         """).format(sql.Literal(limit))
            
#         else:
#             query = sql.SQL("""
#                         SELECT dish, ingredients
#                         FROM dish_table
#                         WHERE ingredients -> 'ingredients' @> %s
#                         """)
#         # Execute the query with the specified ingredient
#         cursor.execute(query, (ingredients, ))

#         # Commit changes to the database
#         conn.commit()

#         # Fetch all the rows that match the query
#         db_rows = cursor.fetchall() 
    
#         # convert the returned dishes to a key-value pair (dish: ingredients)
#         dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

#         return dishes
    
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

#########################
# OLD VERSION USING FLASK
#########################

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

# --------------------figuring out ingredients by dishes --------------------------------



# conn = psycopg2.connect(
#         dbname=Config.DATABASE_NAME,
#         user=Config.DATABASE_USER,
#         password=Config.DATABASE_PW,
#         host=Config.DATABASE_HOST,
#         port=Config.DATABASE_PORT
#     )

# cursor = conn.cursor()

# table_name = "dish_table"
# limit = 2
# dishes = json.dumps('Cahsew Chicken')

# query = sql.SQL("""
#                 SELECT dish, ingredients
#                 FROM {}
#                 WHERE dish -> 'dish' @> %s
#                 LIMIT {}
#                 """).format(sql.Identifier(table_name), sql.Literal(limit))

# # Execute the query with the specified ingredient
# cursor.execute(query, (dishes, ))

# # Commit changes to the database
# conn.commit()

# # Fetch all the rows that match the query
# db_rows = cursor.fetchall() 
# print(f"Number of returned rows: {len(db_rows)}")

# # convert the returned dishes to a key-value pair (dish: ingredients)
# dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}


# --------------------figuring out percent match --------------------------------

# conn = psycopg2.connect(
#         dbname=Config.DATABASE_NAME,
#         user=Config.DATABASE_USER,
#         password=Config.DATABASE_PW,
#         host=Config.DATABASE_HOST,
#         port=Config.DATABASE_PORT
#     )

# cursor = conn.cursor()

# table_name = "dish_table"
# limit = 2
# ingredients = json.dumps(['chicken', 'salt'])


# query = sql.SQL("""
#             SELECT dish, 
#                    ingredients,
#                    jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
#             FROM {}
#             WHERE ingredients -> 'ingredients' @> %s
#             ORDER BY match_percentage DESC
#             LIMIT {}
#             """).format(sql.Identifier(table_name), sql.Literal(limit))

# cursor.execute(query, (ingredients, ingredients))
# conn.commit()

# db_rows = cursor.fetchall()
# print(f"Number of returned rows: {len(db_rows)}")
# print(db_rows[0][2])

# cursor.close()
# conn.close()

# # Convert the returned dishes to a key-value pair (dish: ingredients)
# dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

# # Extract the match percentages
# percent_match = {dish_name: db_rows[i][2] for i, (dish_name, _) in enumerate(dishes.items())}


# match_lengths = [row[2] for row in db_rows]
# print(match_lengths)




# (jsonb_array_length(%s::jsonb->'ingredients')::float / jsonb_array_length(ingredients->'ingredients')::float)

# working length of ingredients in db: jsonb_array_length(ingredients->'ingredients')::float
# working length of inputted ingredients: jsonb_array_length(%s::jsonb)