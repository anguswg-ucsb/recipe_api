import json
from psycopg2 import sql

def _query_directions_by_dish_id(conn, cursor, dish_id, limit):

    """
    SQL query to get directions by dish_id primary key in database.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        dish_id (int or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of dictionary key-value pairs [{"dish_id": "dish id string", "directions" : ["direction1", "direction2"]}]
    """
    
    print(f"Getting ANY directions with dish ID: {dish_id}")
    
    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish_id, dish, directions
                    FROM recipe_table
                    WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish_id, dish, directions
                    FROM recipe_table
                    WHERE dish_id = ANY(%s)
                    """)


    # Execute the query with the specified ingredient
    cursor.execute(query, (dish_id, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # Convert the returned directions to a list of dictionary key-value pairs [{"dish_id": "dish id string", "directions" : ["direction1", "direction2"]}]
    directions = [{"dish_id": db_rows[i][1], "directions": db_rows[i][2]["directions"]} for i in range(0, len(db_rows))]

    return directions


def _query_dishes_by_dish_id(conn, cursor, dish_id, limit):

    """
    SQL query to get dishes by dish_id primary key in database.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        dish_id (int or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of dictionary key-value pairs [{"dish_id": "dish id string", "dish" : "dish name string"}]
    """
    
    print(f"Getting ANY dishes with dish ID: {dish_id}")

    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish, dish_id
                    FROM recipe_table
                    WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish, dish_id
                    FROM recipe_table
                    WHERE dish_id = ANY(%s)
                    """)

    # Execute the query with the specified dish_id
    cursor.execute(query, (dish_id, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # Convert the returned dishes to a list of dictionary key-value pairs [{"dish_id": "dish id string", "dish" : "dish name string"}]
    dishes = [{"dish_id": db_rows[i][1], "dish": db_rows[i][0]["dish"]} for i in range(0, len(db_rows))]

    return dishes


def _query_dishes_by_ingredients(conn, cursor, ingredients, limit):

    """
    SQL query to get dishes that contain the specified ingredients.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        ingredients (str or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of dictionary key-value pairs [{"dish": "dish name string", "ingredients" : ["ingred1", "ingred2"]}]
    """

    print(f"Getting ANY dishes with ingredients(s): {ingredients}")

    # JSON encode the ingredients list
    ingredients = json.dumps(ingredients)
    
    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100


    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM recipe_table
                    WHERE ingredients -> 'ingredients' @> %s
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish, ingredients
                    FROM recipe_table
                    WHERE ingredients -> 'ingredients' @> %s
                    """)


    # Execute the query with the specified ingredient
    cursor.execute(query, (ingredients, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")
    

    # Convert the returned dishes to a list of dictionary key-value pairs [{"dish": "dish name string", "ingredients" : ["ingred1", "ingred2"]}]
    dishes = [{"dish": db_rows[i][0], "ingredients": db_rows[i][1]["ingredients"]} for i in range(0, len(db_rows))]

    return dishes


def _query_dishes_by_name(conn, cursor, name, limit):

    """
    SQL query to get dishes that correspond to the specified dish name.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        name (str): dishes to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of suggested dishes.
    """

    print(f"Getting ANY dishes similar to dish name query: {name}")

    # TODO: Remove from fxn and add to table creation
    # Ensure that the pg_trgm extension is available
    # cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    name = ' '.join([f"{term} <->" for term in name.split()])[:-4]

    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # # If a limit was specified, use it, otherwise return all results
    # if limit:
    #     query = sql.SQL("""
    #                 SELECT dish, SIMILARITY(dish, %s) AS similarity_score
    #                 FROM recipe_table
    #                 ORDER BY similarity_score DESC
    #                 LIMIT {}
    #                 """).format(sql.Literal(limit))

    # else:
    #     query = sql.SQL("""
    #                 SELECT dish, SIMILARITY(dish, %s) AS similarity_score
    #                 FROM recipe_table
    #                 ORDER BY similarity_score DESC
    #                 """)

    if limit:
        query = sql.SQL("""
            SELECT dish
            FROM recipe_table
            WHERE to_tsvector('english', dish) @@ to_tsquery('english', %s || ':*')
            LIMIT {}
            """).format(sql.Literal(limit))

    else:
        query = sql.SQL("""
                    SELECT dish
                    FROM recipe_table
                    WHERE to_tsvector('english', dish) @@ to_tsquery('english', %s || ':*')
                    """).format(sql.Literal(limit))

    # Execute the query with the specified ingredient
    cursor.execute(query, (name, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    for row in db_rows:
        print(f"Dish: {row[0]}, Similarity Score: {row[1]}")

    # Convert the returned dish suggestions to a key-value pair ('dishes': ['dish1', 'dish2', ...]])
    dishes = {'dishes': [db_rows[i][0] for i in range(0, len(db_rows))]}

    return dishes


def _query_recipes_by_ingredients(conn, cursor, ingredients, limit):

    """
    SQL query to get recipes that contain the specified ingredients.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        ingredients (str or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        list: A list of dictionary key-value pairs [{"dish_id": int,  "dish": str, "ingredients" : List[str], "quantities" : List[str], "directions" : List[str]}]
    """

    print(f"Getting ANY dishes with ingredients(s): {ingredients}")

    # JSON encode the ingredients list
    ingredients = json.dumps(ingredients)
    
    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100


    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT dish_id, dish, ingredients, quantities, directions, url, base_url, img
                    FROM recipe_table
                    WHERE ingredients -> 'ingredients' @> %s
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT dish_id, dish, ingredients, quantities, directions, url, base_url, img
                    FROM recipe_table
                    WHERE ingredients -> 'ingredients' @> %s
                    """)


    # Execute the query with the specified ingredient
    cursor.execute(query, (ingredients, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")
    print(f"db_rows: {db_rows}")

    # Convert the returned dishes to a list of dictionary key-value pairs [{"dish": "dish name string", "ingredients" : ["ingred1", "ingred2"]}]
    recipes = [{
        "dish_id": db_rows[i][0], 
        "dish": db_rows[i][1], 
        "ingredients": db_rows[i][2]["ingredients"],
        "quantities": db_rows[i][3]["quantities"],
        "directions": db_rows[i][4]["directions"],
        "url": db_rows[i][5],
        "base_url": db_rows[i][6],
        "img": db_rows[i][7]
        } for i in range(0, len(db_rows))
        ]

    return recipes

# TODO: function needs to be completed
def _query_ingredients_by_dishes(conn, cursor, dishes, limit):

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

    print(f"Getting ANY ingredients with dish name(s): {dishes}")

    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    # TODO: SELECT dish, dish_id
                    # TODO: FROM recipe_table
                    # TODO: WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    # TODO: SELECT dish, dish_id
                    # TODO: FROM recipe_table^^^~
                    # TODO: WHERE dish_id = ANY(%s)
                    """)

    # Execute the query with the specified dish_id
    cursor.execute(query, (dishes, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # TODO: return statement
    # Convert the returned dishes to a key-value pair (dish_id: dish)
    ingredients = {db_rows[i][1]: db_rows[i][0] for i in range(0, len(db_rows))}

    return ingredients


# TODO: data needs to be properly cleaned before this can be tested
# def _query_suggested_ingredients_trgm(conn, cursor, search, limit):

#     """
#     SQL query to get ingredients that contain the specified search string using pg_trgm.

#     Args:
#         conn (psycopg2.connection): Connection to the database.
#         cursor (psycopg2.cursor): Cursor object to interact with the database.
#         search (str): String to search for ingredients.
#         limit (int): Maximum number of results to return.
        
#     Returns:
#         dict: A dictionary of suggested ingredients.
#     """

#     print(f"Getting ANY ingredients with search string: {search}")

#     # TODO: Remove from fxn and add to table creation
#     # Ensure that the pg_trgm extension is available
#     cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

#     # Limit the highest number of results to return
#     if limit and limit > 100:
#         limit = 100

#     # If a limit was specified, use it, otherwise return all results
#     if limit:
#         query = sql.SQL("""
#                     SELECT ingredients, SIMILARITY(ingredients, %s) AS similarity_score
#                     FROM unique_ingredients_table
#                     ORDER BY similarity_score DESC
#                     LIMIT {}
#                     """).format(sql.Literal(limit))

#     else:
#         query = sql.SQL("""
#                     SELECT ingredients, SIMILARITY(ingredients, %s) AS similarity_score
#                     FROM unique_ingredients_table
#                     ORDER BY similarity_score DESC
#                     """)

#     # Execute the query with the specified ingredient
#     cursor.execute(query, (search, ))

#     # Commit changes to the database
#     conn.commit()

#     # Fetch all the rows that match the query
#     db_rows = cursor.fetchall() 
#     for row in db_rows:
#         print(f"Ingredient: {row[0]}, Similarity Score: {row[1]}")
    
#     # Convert the returned ingredient suggestions to a key-value pair ('suggestions': ['ingredient1', 'ingredient2', ...]])
#     ingredients = {'suggestions': [db_rows[i][0] for i in range(0, len(db_rows))]}

#     return ingredients


def _query_suggested_ingredients(conn, cursor, search, limit):

    """
    SQL query to get ingredients that contain the specified search string.

    Args:
        conn (psycopg2.connection): Connection to the database.
        cursor (psycopg2.cursor): Cursor object to interact with the database.
        search (str): String to search for ingredients.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of suggested ingredients.
    """

    print(f"Getting ANY ingredients with search string: {search}")

    # Join search terms with '<->' operators, remove trailing '<->'
    search = ' '.join([f"{term} <->" for term in search.split()])[:-4]

    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
    if limit:
        query = sql.SQL("""
                    SELECT ingredients
                    FROM unique_ingredients_table
                    WHERE to_tsvector('english', ingredients) @@ to_tsquery('english', %s || ':*')
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    SELECT ingredients
                    FROM unique_ingredients_table
                    WHERE to_tsvector('english', ingredients) @@ to_tsquery('english', %s || ':*')
                    """)


    # Execute the query with the specified ingredient
    cursor.execute(query, (search, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")
    
    # Convert the returned ingredient suggestions to a key-value pair ('suggestions': ['ingredient1', 'ingredient2', ...]])
    ingredients = {'suggestions': [db_rows[i][0] for i in range(0, len(db_rows))]}

    return ingredients


# WORKING ON dish search ----------------------------------------------------------------

# import app.config as config
# import psycopg2
# from psycopg2 import sql
# import json

# name = 'chicken'

# limit = 10

# conn = psycopg2.connect(
#         dbname=config.Config.DATABASE_NAME,
#         user=config.Config.DATABASE_USER,
#         password=config.Config.DATABASE_PW,
#         host=config.Config.DATABASE_HOST,
#         port=config.Config.DATABASE_PORT
#     )

# cursor = conn.cursor()

# # Ensure that the pg_trgm extension is available
# cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

# query = sql.SQL("""
#     SELECT dish, SIMILARITY(dish, %s) AS similarity_score
#     FROM dish_table
#     ORDER BY similarity_score DESC
#     LIMIT {}
# """).format(sql.Literal(limit))

# # Execute the query with the specified ingredient
# cursor.execute(query, (name, ))

# # Fetch all the rows that match the query
# db_rows = cursor.fetchall()

# # Print dish names and similarity scores
# for row in db_rows:
#     print(f"Dish: {row[0]}, Similarity Score: {row[1]}")

# # Commit changes to the database
# conn.commit()
# conn.close()

# # Convert the returned dishes to a JSON list
# dishes = {'dishes': [db_rows[i][0] for i in range(0, len(db_rows))]}