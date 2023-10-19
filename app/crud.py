from typing import Union

from fastapi import Depends, FastAPI, HTTPException,  Query
import json
import psycopg2
from psycopg2 import sql

def _query_dishes_by_ingredients(conn, cursor, ingredients, limit = 20):

    """
    SQL query to get dishes that contain the specified ingredients.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        ingredients (str or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dishes and their ingredients.
    """
    
    # if isinstance(ingredients, str):
    #     ingredients = [ingredients]

    # ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"

    # json encode the ingredients list
    ingredients = json.dumps(ingredients)
    
    # limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    table_name = "dish_table"

    # if a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM {}
                    WHERE ingredients -> 'ingredients' @> %s
                    LIMIT {}
                    """).format(sql.Identifier(table_name), sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM {}
                    WHERE ingredients -> 'ingredients' @> %s
                    """).format(sql.Identifier(table_name))


    # Execute the query with the specified ingredient
    cursor.execute(query, (ingredients, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")
    
    # convert the returned dishes to a key-value pair (dish: ingredients)
    dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

    return dishes

# TODO: internal error, function not working properly
def _query_ingredients_by_dishes(conn, cursor, dishes, limit = 20):

    """
    SQL query to get ingredients that correspond to the specified dish name(s).

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        dishes (str or list): dishes to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dishes and their ingredients.
    """
    
    # if isinstance(ingredients, str):
    #     ingredients = [ingredients]

    # ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"

    # json encode the ingredients list
    dishes = json.dumps(dishes)
    
    # limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    table_name = "dish_table"

    # if a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM {}
                    WHERE dish = ANY(%s)
                    LIMIT {}
                    """).format(sql.Identifier(table_name), sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM {}
                    WHERE dish = ANY(%s)
                    """).format(sql.Identifier(table_name))


    # Execute the query with the specified ingredient
    cursor.execute(query, (dishes, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")
    
    # convert the returned dishes to a key-value pair (dish: ingredients)
    dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

    return dishes



def _query_dishes_by_id(conn, cursor, dish_id, limit = 20):
# def get_dishes_by_ingredients(conn, table_name, ingredients, limit = 20):

    """
    SQL query to get dishes by dish_id primary key in database.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        dish_id (int or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dish_id and the dishes name (dish_id: dish)
    """
    
    print(f"Getting ANY dish with a dish_id in {dish_id}")

    # limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # if a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish, dish_id
                    FROM dish_table
                    WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish, dish_id
                    FROM dish_table
                    WHERE dish_id = ANY(%s)
                    """)

    # Execute the query with the specified dish_id
    cursor.execute(query, (dish_id, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 

    print(f"Number of returned rows: {len(db_rows)}")

    # # # convert the returned dishes to a key-value pair (dish: ingredients)
    dishes_by_id = {db_rows[i][1]: db_rows[i][0] for i in range(0, len(db_rows))}

    return dishes_by_id


def _query_directions_by_dish_id(conn, cursor, dish_id, limit = 20):

    """
    SQL query to get directions by dish_id primary key in database.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        dish_id (int or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dish_id and the dish directions (dish_id: directions)
    """
    
    print(f"Getting ANY directions with a dish_id in {dish_id}")
    
    # limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # if a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish_id, dish, directions
                    FROM directions_table
                    WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish_id, dish, directions
                    FROM directions_table
                    WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))


    # Execute the query with the specified ingredient
    cursor.execute(query, (dish_id, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # convert the returned directions to a key-value pair (dish_id: directions)
    directions = {db_rows[i][1]: db_rows[i][2]["directions"] for i in range(0, len(db_rows))}

    return directions

# TODO: ensure this is working correctly
def _query_percent_match_by_ingredients(conn, cursor, ingredients, limit=20):
    """
    SQL query to get dishes that contain the specified ingredients, and percent match to full ingredient list.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        ingredients (str or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dishes and the percent of matching ingredients.
    """
    ingredients = json.dumps(ingredients)
    
    if limit and limit > 100:
        limit = 100

    table_name = "dish_table"

    if limit:
        query = sql.SQL("""
                SELECT dish, 
                    ingredients,
                    jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
                FROM {}
                WHERE ingredients -> 'ingredients' @> %s
                ORDER BY match_percentage DESC
                LIMIT {}
                """).format(sql.Identifier(table_name), sql.Literal(limit))

    else:
        query = sql.SQL("""
                SELECT dish, 
                    ingredients,
                    jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
                FROM {}
                WHERE ingredients -> 'ingredients' @> %s
                ORDER BY match_percentage DESC
                """).format(sql.Identifier(table_name), sql.Literal(limit))

    cursor.execute(query, (ingredients, ingredients))
    conn.commit()

    db_rows = cursor.fetchall()
    print(f"Number of returned rows: {len(db_rows)}")

    cursor.close()
    conn.close()

    # Convert the returned dishes to a key-value pair (dish: ingredients)
    dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

    # Extract the match percentages
    percent_match = {dish_name: db_rows[i][2] for i, (dish_name, _) in enumerate(dishes.items())}

    return percent_match

