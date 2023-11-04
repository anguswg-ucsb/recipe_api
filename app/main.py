
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
