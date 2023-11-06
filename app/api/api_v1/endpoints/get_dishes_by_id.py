from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_dishes_by_id
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_dishes_by_id(
    dish_id: Union[list[int], None] = Query(default=None),
    limit: int = 20
):
    """
    Get dishes by their dish IDs.

    Args:
        dish_id (Union[list[int], None]): List of dish IDs. Defaults to None.
        limit (int): The maximum number of dishes to return. Defaults to 20.

    Returns:
        list: List of dishes matching the specified dish IDs.
    """

    print(f"Getting dishes for dish_id: {dish_id}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query dishes by dish ID
        dishes = _query_dishes_by_id(
            conn = conn, cursor = cursor, dish_id = dish_id, limit = limit
        )
        return dishes

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e

    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()