from fastapi import APIRouter
from app.api.endpoints import example
from app.api.endpoints import json
from app.api.endpoints import text
from app.api.endpoints import definition_verification

# Create a router to group all endpoints
api_router = APIRouter()

# Include routes from each module
api_router.include_router(example.router, prefix="/example", tags=["Example"])
api_router.include_router(json.router, prefix="/json", tags=["JSON"])
api_router.include_router(text.router, prefix="/text", tags=["Text"])
api_router.include_router(definition_verification.router, prefix="/verification", tags=["Verification"])
