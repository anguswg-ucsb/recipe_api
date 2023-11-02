from fastapi import APIRouter, Depends, HTTPException,  Query
import uvicorn
from typing import Union

import psycopg2
from psycopg2 import sql

from app.api.api_v1.endpoints.crud import _query_dishes_by_id
from app.api.db import get_db_conn

router = APIRouter()

# Look up dishes by dish_id
@router.get("/")
def get_dishes_by_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting dishes for dish_id: {dish_id}")

    # Connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        dishes = _query_dishes_by_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
        return dishes
    except Exception as e:
        raise e # Handle database errors
    finally:
        cursor.close()
        conn.close()