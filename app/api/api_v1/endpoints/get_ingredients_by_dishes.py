from fastapi import APIRouter, Depends, HTTPException,  Query
import uvicorn
from typing import Union

import psycopg2
from psycopg2 import sql

from app.api.api_v1.endpoints.crud import _query_ingredients_by_dishes
from app.api.db import get_db_conn

router = APIRouter()

# Look up ingredients by dishes
@router.get("/")
def get_ingredients_by_dishes(dishes: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting ingredients for dishes: {dishes}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        ingredients = _query_ingredients_by_dishes(conn=conn, cursor=cursor, dishes=dishes, limit=limit)
        return ingredients
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()