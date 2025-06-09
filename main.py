from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config import CONVERTED_DIR, setup_directories
from routes import conversion, files
import uvicorn

# Setup directories
setup_directories()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversion.router)
app.include_router(files.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
