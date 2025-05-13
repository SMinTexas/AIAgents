from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify required environment variables
required_env_vars = [
    "GOOGLE_MAPS_API_KEY",
    "OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "WEATHER_API_KEY"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from orchestrator import router as orchestrator_router

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the orchestrator router (handles trip planning, weather, and recommendations)
app.include_router(orchestrator_router)

@app.get("/")
def home():
    return {"message": "AI Travel Planner API is running"}
