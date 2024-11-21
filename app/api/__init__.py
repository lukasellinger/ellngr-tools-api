from fastapi import APIRouter
from app.api.endpoints import example

# Create a router to group all endpoints
api_router = APIRouter()

# Include routes from each module
api_router.include_router(example.router, prefix="/example", tags=["Example"])
