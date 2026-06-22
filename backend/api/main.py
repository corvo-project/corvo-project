from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from .routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="OCR Document API")

app.include_router(router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# app.mount("/static", StaticFiles(directory="/home/alessio/corvo/backend/data/documents"), name="static")
