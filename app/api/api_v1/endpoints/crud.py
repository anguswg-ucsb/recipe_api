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
        dict: A dictionary of dish_id and the dish directions (dish_id: directions)
    """
    
    print(f"Getting ANY directions with dish ID: {dish_id}")
    
    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
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
                    """)


    # Execute the query with the specified ingredient
    cursor.execute(query, (dish_id, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # Convert the returned directions to a key-value pair (dish_id: directions)
    directions = {db_rows[i][1]: db_rows[i][2]["directions"] for i in range(0, len(db_rows))}

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
        dict: A dictionary of dish_id and the dishes name (dish_id: dish)
    """
    
    print(f"Getting ANY dishes with dish ID: {dish_id}")

    # Limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

    # If a limit was specified, use it, otherwise return all results
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

    # Convert the returned dishes to a key-value pair (dish_id: dish)
    dishes = {db_rows[i][1]: db_rows[i][0] for i in range(0, len(db_rows))}

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
        dict: A dictionary of dishes and their ingredients.
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
    print(f"Number of returned rows: {len(db_rows)}")
    
    # Convert the returned dishes to a key-value pair (dish: ingredients)
    dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

    return dishes



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
                    # TODO: FROM dish_table
                    # TODO: WHERE dish_id = ANY(%s)
                    LIMIT {}
                    """).format(sql.Literal(limit))
        
    else:
        query = sql.SQL("""
                    # TODO: SELECT dish, dish_id
                    # TODO: FROM dish_table
                    # TODO: WHERE dish_id = ANY(%s)
                    """)

    # Execute the query with the specified dish_id
    cursor.execute(query, (dishes, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cursor.fetchall() 
    print(f"Number of returned rows: {len(db_rows)}")

    # Convert the returned dishes to a key-value pair (dish_id: dish)
    ingredients = {db_rows[i][1]: db_rows[i][0] for i in range(0, len(db_rows))}

    return ingredients



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



# TODO: ensure this is working correctly
# TODO: needs an endpoint file
# TODO: needs a route in api
# def _query_percent_match_by_ingredients(conn, cursor, ingredients, limit):
#     """
#     SQL query to get dishes that contain the specified ingredients, and percent match to full ingredient list.

#     Args:
#         conn (psycopg2.connection): Connection to the database.
#         cursor (psycopg2.cursor): Cursor object to interact with the database.
#         ingredients (str or list): Ingredients to search for.
#         limit (int): Maximum number of results to return.
        
#     Returns:
#         dict: A dictionary of dishes and the percent of matching ingredients.
#     """

#    print(f"Getting ANY dishes AND percent match with ingredient(s): {ingredients}")

#     ingredients = json.dumps(ingredients)
    
#     if limit and limit > 100:
#         limit = 100

#     table_name = "dish_table"

#     if limit:
#         query = sql.SQL("""
#                 SELECT dish, 
#                     ingredients,
#                     jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
#                 FROM {}
#                 WHERE ingredients -> 'ingredients' @> %s
#                 ORDER BY match_percentage DESC
#                 LIMIT {}
#                 """).format(sql.Identifier(table_name), sql.Literal(limit))

#     else:
#         query = sql.SQL("""
#                 SELECT dish, 
#                     ingredients,
#                     jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
#                 FROM {}
#                 WHERE ingredients -> 'ingredients' @> %s
#                 ORDER BY match_percentage DESC
#                 """).format(sql.Identifier(table_name), sql.Literal(limit))

#     cursor.execute(query, (ingredients, ingredients))
#     conn.commit()

#     db_rows = cursor.fetchall()
#     print(f"Number of returned rows: {len(db_rows)}")

#     cursor.close()
#     conn.close()

#     # Convert the returned dishes to a key-value pair (dish: ingredients)
#     dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}

#     # Extract the match percentages
#     percent_match = {dish_name: db_rows[i][2] for i, (dish_name, _) in enumerate(dishes.items())}

#     return percent_match






# WORKING ON PCT MATCH ----------------------------------------------------------------

# import app.config as config
# import psycopg2
# from psycopg2 import sql
# import json

# ingredients = 'chicken'
# ingredients = json.dumps(ingredients)

# limit = 3

# conn = psycopg2.connect(
#         dbname=config.Config.DATABASE_NAME,
#         user=config.Config.DATABASE_USER,
#         password=config.Config.DATABASE_PW,
#         host=config.Config.DATABASE_HOST,
#         port=config.Config.DATABASE_PORT
#     )

# cursor = conn.cursor()

# query = sql.SQL("""
#         SELECT dish, 
#             ingredients,
#             jsonb_array_length(%s::jsonb) / jsonb_array_length(ingredients->'ingredients')::float as match_percentage
#         FROM dish_table
#         WHERE ingredients -> 'ingredients' @> %s
#         ORDER BY match_percentage DESC
#         LIMIT {}
#         """).format(sql.Literal(limit))

# # Execute the query with the specified ingredient
# cursor.execute(query, (ingredients, ))

# # Fetch all the rows that match the query
# db_rows = cursor.fetchall()
# print(f"Number of returned rows: {len(db_rows)}")

# # Commit changes to the database
# conn.commit()
# conn.close()

# # Convert the returned dishes to a JSON list
# ingredients = {'suggestions': [db_rows[i][0] for i in range(0, len(db_rows))]}

