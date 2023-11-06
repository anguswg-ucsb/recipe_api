from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_suggested_ingredients
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_suggested_ingredients(
    search: Union[str, None] = Query(default=None),
    limit: int = 10
):
    """
    Get suggested ingredients based on a search query.

    Args:
        search (Union[str, None]): The search query. Defaults to None.
        limit (int): The maximum number of ingredients to return. Defaults to 10.

    Returns:
        list: List of suggested ingredients.
    """

    print(f"Getting ingredients for search: {search}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query suggested ingredients by search string
        ingredients = _query_suggested_ingredients(
            conn = conn, cursor = cursor, search = search, limit = limit
        )
        return ingredients

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e

    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()