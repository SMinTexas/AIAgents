from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from orchestrator import router as orchestrator_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the orchestrator router (handles trip planning, traffic, weather, and recommendations)
app.include_router(orchestrator_router)

@app.get("/")
def home():
    return {"message": "AI Travel Planner API is running"}
