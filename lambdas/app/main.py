from fastapi import FastAPI
from app.api.api_v1.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

from mangum import Mangum

# instantiate app
app = FastAPI()

# Allow all origins
origins = ["*"]

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# tester method
@app.get("/")
def root():
    return {"Root": "Home route"}

# import router and add to app
app.include_router(api_router, prefix="/api/v1")

# wrap app in mangum for running API within Lambda
handler = Mangum(app)
