
from fastapi import FastAPI
from app.api.api_v1.api import router as api_router

from mangum import Mangum

import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"Root": "Home route"}

app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

###############################

# # instantiate FastAPI app
# app = FastAPI()

# # # wrao the app in Mangum for AWS Lambda
# # handler = Mangum(app)

# # function that makes a database connection
# def get_db_conn():
#     conn = psycopg2.connect(
#         dbname=Config.DATABASE_NAME,
#         user=Config.DATABASE_USER,
#         password=Config.DATABASE_PW,
#         host=Config.DATABASE_HOST,
#         port=Config.DATABASE_PORT
#     )
#     return conn

# # look up dishes by ingredients resource
# @app.get("/dishes-by-ingredients/")
# def get_dishes_by_ingredients(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
#     print(f"Making get request w/ {ingredients}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         dishes = crud._query_dishes_by_ingredients(conn=conn, cursor=cursor, ingredients=ingredients, limit=limit)
#         return dishes
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

# # TODO: internal error, function not working properly
# # look up directions by dish_name
# @app.get("/ingredients-by-dishes/")
# def get_ingredients_by_dishes(dishes: Union[list[str], None] = Query(default=None), limit: int = 20):
    
#     print(f"Making get request w/ {dishes}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         dishes = crud._query_ingredients_by_dishes(conn=conn, cursor=cursor, dishes=dishes, limit=limit)
#         return dishes
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

# # look up dishes by dish_id
# @app.get("/dishes-by-id/")
# def get_dishes_by_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
#     print(f"Getting dishes by dish_id {dish_id}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         directions = crud._query_dishes_by_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
#         return directions
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

# # look up directions by ingredients resource
# @app.get("/directions-by-id/")
# def get_directions_by_dish_id(dish_id: Union[list[int], None] = Query(default=None), limit: int = 20):
    
#     print(f"Getting directions by dish_id {dish_id}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         directions = crud._query_directions_by_dish_id(conn=conn, cursor=cursor, dish_id=dish_id, limit=limit)
#         return directions
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

# # look up dishes and match percentage by ingredients resource
# @app.get("/percent_match-by-ingredients/")
# def get_percent_match_by_ingredients(ingredients: Union[list[str], None] = Query(default=None), limit: int = 20):
    
#     print(f"Making get request to w/ {ingredients}")
#     conn = get_db_conn()
#     cursor = conn.cursor()
    
#     try:
#         percent_match = crud._query_percent_match_by_ingredients(conn=conn, cursor=cursor, ingredients=ingredients, limit=limit)
#         return percent_match
#     except Exception as e:
#         # Handle database errors
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

# if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8080)
