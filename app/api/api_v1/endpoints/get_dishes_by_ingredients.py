from fastapi import APIRouter, Depends, HTTPException,  Query
import uvicorn
from typing import Union

import psycopg2
from psycopg2 import sql

from app.api.api_v1.endpoints.crud import _query_dishes_by_ingredients
from app.api.db import get_db_conn

router = APIRouter()

# Look up dishes by ingredients
@router.get("/")
def get_dishes_by_ingredients(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting dishes for ingredients: {ingredients}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        dishes = _query_dishes_by_ingredients(conn=conn, cursor=cursor, ingredients=ingredients, limit=limit)
        return dishes
    except Exception as e:
        raise e # Handle database errors
    finally:
        cursor.close()
        conn.close()
