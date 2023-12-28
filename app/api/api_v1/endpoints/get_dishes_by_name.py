from fastapi import APIRouter, Query
from typing import Union
from app.api.api_v1.endpoints.crud import _query_dishes_by_name
from app.api.db import get_db_conn

router = APIRouter()

@router.get("/")
def get_dishes_by_name(
    name: Union[str, None] = Query(default=None),
    limit: int = 10
):
    """
    Get dishes that either exactly or closely match the given dish name query.

    Args:
        dishes (Union[list[str], None]): The dish name query. Defaults to None.
        limit (int): The maximum number of dishes to return. Defaults to 20.

    Returns:
        list: List of dishes related to the specified query.
    """

    print(f"Getting dishes for dish name query: {name}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # Try to query dishes by dish name
        dishes = _query_dishes_by_name(
            conn = conn, cursor = cursor, name = name, limit = limit
        )
        return dishes

    except Exception as e:
        # Handle any exceptions that occur during the query
        raise e
        
    finally:
        # Close the cursor and connection, regardless of whether an exception occurred
        cursor.close()
        conn.close()