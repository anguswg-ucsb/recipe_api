from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_recipes_by_ingredients
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_recipes_by_ingredients(
    ingredients: Union[list[str], None] = Query(default=None),
    limit: int = 5
):
    """
    Get a list of recipes that contain the specified ingredients.

    Args:
        ingredients (Union[list[str], None]): List of ingredient names. Defaults to None.
        limit (int): The maximum number of dishes to return. Defaults to 20.

    Returns:
        list: List of recipes containing the specified ingredients.
    """

    print(f"Getting dishes for ingredients: {ingredients}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query dishes by ingredients
        recipes = _query_recipes_by_ingredients(
            conn = conn, cursor = cursor, ingredients = ingredients, limit = limit
        )
        return recipes

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e
        
    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()
