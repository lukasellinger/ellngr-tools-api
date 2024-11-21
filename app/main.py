from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router

app = FastAPI(root_path='/api')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost",
                   "http://localhost:3000",
                   "https://tools.ellngr.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
