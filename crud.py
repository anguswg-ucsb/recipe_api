from sqlalchemy.orm import Session
from sqlalchemy import sql


def get_dishes_by_ingredients(db: Session, ingredients: list, limit: int = 20):
# def get_dishes_by_ingredients(conn, table_name, ingredients, limit = 20):

    """
    Get dishes from the database that contain the specified ingredients.

    Args:
        db (Session): Connection to the database.
        ingredients (str or list): Ingredients to search for.
        limit (int): Maximum number of results to return.
        
    Returns:
        dict: A dictionary of dishes and their ingredients.
    """
    
    if isinstance(ingredients, str):
        ingredients = [ingredients]

    ingredients =  "[" + ', '.join(f'"{ingredient}"' for ingredient in ingredients) + "]"

    # limit the highest number of results to return
    if limit and limit > 100:
        limit = 100

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

    # Create cursor object to interact with the database
    cur = conn.cursor()

    # Execute the query with the specified ingredient
    cur.execute(query, (ingredients, ))

    # Commit changes to the database
    conn.commit()

    # Fetch all the rows that match the query
    db_rows = cur.fetchall() 
    
    # convert the returned dishes to a key-value pair (dish: ingredients)
    dishes = {db_rows[i][0]: db_rows[i][1] for i in range(0, len(db_rows))}
    
    cur.close()

    return dishes