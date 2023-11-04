from fastapi import APIRouter, Depends, HTTPException,  Query
import uvicorn
from typing import Union

import psycopg2
from psycopg2 import sql

from app.api.api_v1.endpoints.crud import _query_suggested_ingredients
from app.api.db import get_db_conn

router = APIRouter()

# Look up ingredients by search
@router.get("/")
def get_suggested_ingredients(search: Union[str, None] = Query(default=None), limit: int = 10):
    
    print(f"Getting ingredients for search: {search}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        ingredients = _query_suggested_ingredients(conn=conn, cursor=cursor, search=search, limit=limit)
        return ingredients
    except Exception as e:
        raise e # Handle database errors
    finally:
        cursor.close()
        conn.close()