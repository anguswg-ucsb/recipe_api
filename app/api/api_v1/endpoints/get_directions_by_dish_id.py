from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_directions_by_dish_id
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_directions_by_dish_id(
    dish_id: Union[list[int], None] = Query(default=None),
    limit: int = 20
):
    """
    Get directions for a specific dish by its dish ID.

    Args:
        dish_id (Union[list[int], None]): List of dish IDs. Defaults to None.
        limit (int): The maximum number of directions to return. Defaults to 20.

    Returns:
        list: List of directions for the specified dish IDs.
    """

    print(f"Getting directions for dish_id {dish_id}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query directions by dish ID
        directions = _query_directions_by_dish_id(
              conn = conn, cursor = cursor, dish_id = dish_id, limit = limit
        )
        return directions

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e

    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()