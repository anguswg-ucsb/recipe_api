from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_ingredients_by_dishes
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_ingredients_by_dishes(
    dishes: Union[list[str], None] = Query(default=None),
    limit: int = 20
):
    """
    Get ingredients for a list of dishes.

    Args:
        dishes (Union[list[str], None]): List of dish names. Defaults to None.
        limit (int): The maximum number of dishes and their corresponding ingredients to return. Defaults to 20.

    Returns:
        list: List of ingredients for the given dishes.
    """

    print(f"Getting ingredients for dishes: {dishes}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query ingredients by dishes
        ingredients = _query_ingredients_by_dishes(
            conn = conn, cursor = cursor, dishes = dishes, limit = limit
        )
        return ingredients

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e

    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()