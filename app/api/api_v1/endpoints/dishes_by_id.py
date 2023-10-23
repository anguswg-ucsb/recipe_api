from fastapi import APIRouter, Depends, HTTPException,  Query
import uvicorn
from typing import Union

import psycopg2
from psycopg2 import sql

# from app.api.api_v1.endpoints.crud import _query_dishes_by_id, get_db_conn
from app.api.api_v1.endpoints.crud import _query_dishes_by_id
from app.api.db import get_db_conn

# import app.config as config

router = APIRouter()

# look up dishes by dish_id
# @router.get("/dishes-by-id/")
@router.get("/")
def get_dishes_by_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
    print(f"Getting dishes by dish_id {dish_id}")

    # conn = get_db_conn(
    #     db_name=config.Config.DATABASE_NAME,
    #     db_host=config.Config.DATABASE_HOST, 
    #     db_user=config.Config.DATABASE_USER, 
    #     db_pw=config.Config.DATABASE_PW, 
    #     db_port=config.Config.DATABASE_PORT
    #     )
    
    # cursor = conn.cursor()

    # connect to the DB
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        directions = _query_dishes_by_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
        return directions
    except Exception as e:
        # Handle database errors
        raise e
    finally:
        cursor.close()
        conn.close()